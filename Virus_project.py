from __future__ import annotations
import hashlib
import json
import shutil
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

BUFFER_SIZE = 1024 * 1024
LOG_FILE = "scan.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
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

def sha256_file(file_path: Path) -> Optional[str]:
    """Calcula o hash SHA256 de um ficheiro. Retorna None em caso de erro."""
    try:
        h = hashlib.sha256()
        with file_path.open("rb") as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                h.update(chunk)
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

def scan_file(file_path: Path, signatures: Dict[str, str]) -> ScanResult:
    """Analisa um ficheiro individual contra as assinaturas de malware."""
    if not file_path.is_file():
        return ScanResult(file_path=str(file_path), status="skip", reason="não é ficheiro")

    digest = sha256_file(file_path)
    if digest is None:
        return ScanResult(file_path=str(file_path), status="skip", reason="erro ao ler ficheiro")

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

def scan_directory(root: Path, signatures: Dict[str, str]) -> List[ScanResult]:
    """Varre recursivamente um diretório e retorna os resultados."""
    results: List[ScanResult] = []
    try:
        for path in root.rglob("*"):
            if path.is_file():
                results.append(scan_file(path, signatures))
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
        logger.error(f"Erro ao quarentena {file_path}: {e}")
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

def main() -> None:
    """Interface CLI para varredura de antivírus."""
    logger.info("=== Antivírus Projeto — Varredura CLI ===")
    target_dir_input = input("Diretório para escanear: ").strip()
    target_dir = Path(target_dir_input)

    if not target_dir.exists() or not target_dir.is_dir():
        logger.error(f"Diretório inválido: {target_dir}")
        print("Diretório inválido.")
        return

    signatures = load_signatures(Path("signatures.json"))
    if not signatures:
        logger.warning("Nenhuma assinatura carregada!")

    results = scan_directory(target_dir, signatures)
    infected = [r for r in results if r.status == "infected"]
    clean = [r for r in results if r.status == "clean"]

    print(f"\nArquivos limpos: {len(clean)}")
    print(f"Arquivos suspeitos/infectados: {len(infected)}\n")

    for item in infected:
        print(f"[INFECTADO] {item.file_path} -> {item.reason}")

    if save_report(results, Path("output/scan_report.json")):
        print(f"Relatório salvo em output/scan_report.json")

    if infected:
        choice = input("\nMover infectados para quarentena? (s/n): ").strip().lower()
        if choice == "s":
            quarantine_dir = Path("quarantine")
            quarantined = 0
            for item in infected:
                if quarantine_file(Path(item.file_path), quarantine_dir):
                    quarantined += 1
            print(f"Quarentena concluída: {quarantined} ficheiro(s) movido(s).")

    logger.info("=== Varredura concluída ===")

if __name__ == "__main__":
    main()
