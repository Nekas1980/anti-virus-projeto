#!/usr/bin/env python3
"""
VirusTotal Signature Updater

Utility para atualizar assinaturas de malware com dados do VirusTotal.
Requer API key: https://www.virustotal.com/gui/
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_virustotal_key() -> Optional[str]:
    """Retorna a API key do VirusTotal de variável de ambiente."""
    key = os.getenv("VIRUSTOTAL_API_KEY")
    if not key:
        logger.warning("Variável VIRUSTOTAL_API_KEY não definida")
        logger.info("Configure com: export VIRUSTOTAL_API_KEY='sua_chave'")
    return key


def fetch_vt_hash_info(file_hash: str, api_key: str) -> Optional[Dict]:
    """Busca informações de um hash no VirusTotal."""
    try:
        import requests
    except ImportError:
        logger.error("Módulo 'requests' não disponível. Instale com: pip install requests")
        return None

    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {"x-apikey": api_key}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.debug(f"Hash não encontrado no VirusTotal: {file_hash}")
            return None
        else:
            logger.warning(f"Erro VirusTotal (status {response.status_code}): {response.text}")
            return None
    except Exception as e:
        logger.error(f"Erro ao consultar VirusTotal: {e}")
        return None


def is_malware(vt_data: Dict) -> bool:
    """Determina se um arquivo é malware baseado em detecções."""
    try:
        attributes = vt_data.get("data", {}).get("attributes", {})
        stats = attributes.get("last_analysis_stats", {})
        malicious = stats.get("malicious", 0)
        return malicious > 0
    except Exception:
        return False


def extract_malware_name(vt_data: Dict) -> Optional[str]:
    """Extrai nome do malware de detecções do VirusTotal."""
    try:
        attributes = vt_data.get("data", {}).get("attributes", {})
        results = attributes.get("last_analysis_results", {})

        for vendor, detection in results.items():
            if detection.get("category") == "malware":
                name = detection.get("engine_name", "")
                if name:
                    return f"{vendor}:{detection.get('result', 'Unknown')}"

        if results:
            first_detection = next(iter(results.values()), {})
            return first_detection.get("result", "Unknown")

        return None
    except Exception:
        return None


def load_signatures(signature_file: Path) -> Dict[str, str]:
    """Carrega assinaturas existentes."""
    if not signature_file.exists():
        return {}
    try:
        with signature_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("malware_hashes", {})
    except Exception as e:
        logger.error(f"Erro ao carregar assinaturas: {e}")
        return {}


def save_signatures(signatures: Dict[str, str], signature_file: Path) -> bool:
    """Salva assinaturas atualizadas."""
    try:
        signature_file.parent.mkdir(parents=True, exist_ok=True)
        data = {"malware_hashes": signatures}
        with signature_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Assinaturas salvas em {signature_file}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar assinaturas: {e}")
        return False


def update_single_hash(file_hash: str, signature_file: Path = Path("signatures.json")) -> bool:
    """Atualiza uma assinatura individual no VirusTotal."""
    api_key = get_virustotal_key()
    if not api_key:
        logger.error("API key do VirusTotal necessária")
        return False

    logger.info(f"Consultando VirusTotal para hash: {file_hash}")
    vt_data = fetch_vt_hash_info(file_hash, api_key)

    if not vt_data:
        logger.info(f"Não foi possível obter dados para: {file_hash}")
        return False

    if is_malware(vt_data):
        malware_name = extract_malware_name(vt_data)
        signatures = load_signatures(signature_file)
        signatures[file_hash] = malware_name or "Unknown"
        logger.info(f"✓ Detectado como malware: {malware_name}")
        return save_signatures(signatures, signature_file)
    else:
        logger.info(f"Arquivo limpo (nenhuma detecção): {file_hash}")
        return True


def batch_update(hashes: List[str], signature_file: Path = Path("signatures.json")) -> int:
    """Atualiza múltiplos hashes. Retorna quantidade adicionada."""
    api_key = get_virustotal_key()
    if not api_key:
        logger.error("API key do VirusTotal necessária")
        return 0

    signatures = load_signatures(signature_file)
    added = 0

    for i, file_hash in enumerate(hashes, 1):
        if file_hash in signatures:
            logger.debug(f"[{i}/{len(hashes)}] Já existe: {file_hash}")
            continue

        logger.info(f"[{i}/{len(hashes)}] Consultando: {file_hash}")
        vt_data = fetch_vt_hash_info(file_hash, api_key)

        if vt_data and is_malware(vt_data):
            malware_name = extract_malware_name(vt_data)
            signatures[file_hash] = malware_name or "Unknown"
            added += 1
            logger.info(f"  ✓ Adicionado: {malware_name}")

    if added > 0:
        save_signatures(signatures, signature_file)
        logger.info(f"Total adicionado: {added} assinatura(s)")

    return added


def main() -> None:
    """Interface CLI para atualizar assinaturas."""
    logger.info("=== VirusTotal Signature Updater ===")

    api_key = get_virustotal_key()
    if not api_key:
        logger.error("VIRUSTOTAL_API_KEY não definida. Configure e tente novamente.")
        return

    logger.info("API key carregada (primeiros 8 caracteres: " + api_key[:8] + "...)")

    choice = input("\n1. Consultar um hash\n2. Sair\nEscolha: ").strip()

    if choice == "1":
        file_hash = input("Hash SHA256: ").strip()
        if len(file_hash) == 64:
            update_single_hash(file_hash)
        else:
            logger.error("Hash SHA256 deve ter 64 caracteres")
    else:
        logger.info("Saindo...")


if __name__ == "__main__":
    main()
