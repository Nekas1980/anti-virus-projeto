from __future__ import annotations
import hashlib
import json
import os
import shutil
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from config import LOG, PATHS, SCAN
from exclusion_matcher import ExclusionMatcher
from hash_cache import HashCache

BUFFER_SIZE = SCAN["buffer_size"]
LOG_FILE = str(PATHS["log_file"])
DEFAULT_FILE_TIMEOUT = SCAN["file_timeout_seconds"]

logging.basicConfig(
    level=getattr(logging, LOG["level"]),
    format=LOG["format"],
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

@dataclass
class ScanResult:
    file_path: str
    status: str
    reason: str = ""
    sha256: str = ""

def sha256_file(file_path: Path, timeout: Optional[float] = None) -> Optional[str]:
    """Calcula o hash SHA256 de um ficheiro.

    Retorna None em caso de erro de I/O, ou se exceder o timeout em segundos.
    """
    if timeout is not None and timeout <= 0:
        logger.warning(f"Timeout ao ler {file_path} (>{timeout}s)")
        return None
    try:
        h = hashlib.sha256()
        start = time.monotonic()
        with file_path.open("rb") as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                h.update(chunk)
                if timeout is not None and (time.monotonic() - start) > timeout:
                    logger.warning(f"Timeout ao ler {file_path} (>{timeout}s)")
                    return None
        return h.hexdigest()
    except (IOError, OSError) as e:
        logger.warning(f"Erro ao ler {file_path}: {e}")
        return None

def load_signatures(signature_file: Path) -> Dict[str, str]:
    """Carrega assinaturas de malware do arquivo JSON."""
    if not signature_file.exists():
        logger.warning(f"Arquivo de assinaturas não encontrado: {signature_file}")
        return {}
    try:
        with signature_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        sigs = data.get("malware_hashes", {})
        logger.info(f"Carregadas {len(sigs)} assinaturas de {signature_file}")
        return sigs
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Erro ao carregar assinaturas: {e}")
        return {}

def save_signatures(signatures: Dict[str, str], signature_file: Path) -> bool:
    """Guarda assinaturas de malware no ficheiro JSON. Retorna True se bem-sucedido."""
    try:
        signature_file.parent.mkdir(parents=True, exist_ok=True)
        data = {"malware_hashes": signatures}
        with signature_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Assinaturas salvas em {signature_file}")
        return True
    except (IOError, OSError) as e:
        logger.error(f"Erro ao salvar assinaturas: {e}")
        return False

def add_signature(file_hash: str, malware_name: str, signature_file: Path = Path("signatures.json")) -> bool:
    """Adiciona uma nova assinatura de malware. Retorna True se bem-sucedido."""
    try:
        signatures = load_signatures(signature_file)
        if file_hash in signatures:
            logger.warning(f"Assinatura já existe: {file_hash}")
            return False
        signatures[file_hash] = malware_name
        if save_signatures(signatures, signature_file):
            logger.info(f"Assinatura adicionada: {file_hash} → {malware_name}")
            return True
        return False
    except (IOError, OSError, json.JSONDecodeError) as e:
        logger.error(f"Erro ao adicionar assinatura: {e}")
        return False

def load_exclusions(exclusion_file: Path) -> List[str]:
    """Carrega padrões de exclusão do arquivo JSON."""
    if not exclusion_file.exists():
        logger.info(f"Arquivo de exclusões não encontrado, usando padrões padrão")
        return get_default_exclusions()
    try:
        with exclusion_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        patterns = data.get("exclusion_patterns", [])
        logger.info(f"Carregados {len(patterns)} padrões de exclusão")
        return patterns
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Erro ao carregar exclusões, usando padrões padrão: {e}")
        return get_default_exclusions()

def get_default_exclusions() -> List[str]:
    """Retorna padrões de exclusão padrão."""
    return [
        "node_modules",
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".idea",
        ".vscode",
        "*.egg-info",
        ".DS_Store",
        "Thumbs.db",
        ".env",
    ]

def should_skip_path(path: Path, exclusion_patterns: List[str]) -> bool:
    """Verifica se um caminho deve ser ignorado baseado nos padrões de exclusão.

    Para varreduras grandes, prefira `ExclusionMatcher` directamente para
    evitar recompilar regex a cada chamada.
    """
    return ExclusionMatcher(exclusion_patterns).matches(path)

def scan_file(
    file_path: Path,
    signatures: Dict[str, str],
    cache: Optional["HashCache"] = None,
    timeout: Optional[float] = DEFAULT_FILE_TIMEOUT,
) -> ScanResult:
    """Analisa um ficheiro individual contra as assinaturas de malware."""
    if not file_path.is_file():
        return ScanResult(file_path=str(file_path), status="skip", reason="não é ficheiro")

    digest: Optional[str] = None
    if cache is not None:
        digest = cache.get(file_path)

    if digest is None:
        digest = sha256_file(file_path, timeout=timeout)
        if digest is None:
            return ScanResult(file_path=str(file_path), status="skip", reason="erro ou timeout")
        if cache is not None:
            cache.set(file_path, digest)

    threat_name = signatures.get(digest)
    if threat_name:
        logger.warning(f"INFECTADO: {file_path} → {threat_name}")
        return ScanResult(
            file_path=str(file_path),
            status="infected",
            reason=threat_name,
            sha256=digest,
        )
    return ScanResult(
        file_path=str(file_path),
        status="clean",
        sha256=digest,
    )

def scan_directory(
    root: Path,
    signatures: Dict[str, str],
    exclusions: List[str],
    cache: Optional["HashCache"] = None,
) -> List[ScanResult]:
    """Varre recursivamente um diretório e retorna os resultados, respeitando exclusões."""
    matcher = ExclusionMatcher(exclusions)
    results: List[ScanResult] = []
    try:
        for current_root, dirs, files in os.walk(root):
            # Podar diretórios excluídos para evitar entrar neles (ex: node_modules)
            # Modificar dirs in-place para que o os.walk não os visite
            i = len(dirs) - 1
            while i >= 0:
                d_path = Path(current_root) / dirs[i]
                if matcher.matches(d_path):
                    logger.debug(f"Ignorando diretório (exclusão): {d_path}")
                    del dirs[i]
                i -= 1

            for f in files:
                f_path = Path(current_root) / f
                if matcher.matches(f_path):
                    logger.debug(f"Ignorando ficheiro (exclusão): {f_path}")
                    continue
                results.append(scan_file(f_path, signatures, cache=cache))
    except (IOError, OSError) as e:
        logger.error(f"Erro ao varrer diretório {root}: {e}")
    return results

def quarantine_file(file_path: Path, quarantine_dir: Path) -> Optional[Path]:
    """Move um ficheiro infectado para quarentena. Retorna o caminho de destino."""
    try:
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        target = quarantine_dir / file_path.name
        counter = 1
        while target.exists():
            target = quarantine_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
            counter += 1
        shutil.move(str(file_path), str(target))
        logger.info(f"Quarentena: {file_path} → {target}")
        return target
    except (IOError, OSError) as e:
        logger.error(f"Erro ao mover para quarentena {file_path}: {e}")
        return None

def save_report(results: List[ScanResult], output_file: Path) -> bool:
    """Salva relatório de scan em JSON. Retorna True se bem-sucedido."""
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "file_path": r.file_path,
                "status": r.status,
                "reason": r.reason,
                "sha256": r.sha256,
            }
            for r in results
        ]
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        logger.info(f"Relatório salvo em {output_file}")
        return True
    except (IOError, OSError, json.JSONDecodeError) as e:
        logger.error(f"Erro ao salvar relatório: {e}")
        return False

def main() -> None:  # pragma: no cover
    """Interface CLI para varredura de antivírus."""
    logger.info("=== Antivírus Projeto — Varredura CLI ===")
    target_dir_input = input("Diretório para escanear: ").strip()
    target_dir = Path(target_dir_input)

    if not target_dir.exists() or not target_dir.is_dir():
        logger.error(f"Diretório inválido: {target_dir}")
        print("Diretório inválido.")
        return

    signatures = load_signatures(PATHS["signatures"])
    if not signatures:
        logger.warning("Nenhuma assinatura carregada!")

    exclusions = load_exclusions(PATHS["exclusions"])
    logger.info(f"Usando {len(exclusions)} padrões de exclusão")

    cache = HashCache(PATHS["scan_cache"]) if SCAN["cache_enabled"] else None

    try:
        results = scan_directory(target_dir, signatures, exclusions, cache=cache)
    finally:
        if cache is not None:
            cache.close()

    infected = [r for r in results if r.status == "infected"]
    clean = [r for r in results if r.status == "clean"]

    print(f"\nArquivos limpos: {len(clean)}")
    print(f"Arquivos suspeitos/infectados: {len(infected)}\n")

    for item in infected:
        print(f"[INFECTADO] {item.file_path} -> {item.reason}")

    report_path = PATHS["output_dir"] / "scan_report.json"
    if save_report(results, report_path):
        print(f"Relatório salvo em {report_path}")

    if infected:
        choice = input("\nMover infectados para quarentena? (s/n): ").strip().lower()
        if choice == "s":
            quarantine_dir = PATHS["quarantine_dir"]
            quarantined = 0
            for item in infected:
                if quarantine_file(Path(item.file_path), quarantine_dir):
                    quarantined += 1
            print(f"Quarentena concluída: {quarantined} ficheiro(s) movido(s).")

    logger.info("=== Varredura concluída ===")

if __name__ == "__main__":  # pragma: no cover
    main()
