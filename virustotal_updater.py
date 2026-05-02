#!/usr/bin/env python3
"""
VirusTotal Signature Updater.

Consulta a API v3 do VirusTotal para enriquecer `signatures.json` com
classificações de malware. Inclui:

- Cache local SQLite (`vt_cache.VTCache`) com TTL — evita requeries.
- Rate limiter de 4 req/min (configurável) — respeita o tier gratuito.
- Retry com exponential backoff em falhas transitórias.
- Deduplicação dos hashes pedidos antes de bater na API.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from config import PATHS, VIRUSTOTAL
from rate_limiter import RateLimiter, retry
from vt_cache import VTCache

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

_LIMITER = RateLimiter(max_per_minute=VIRUSTOTAL["rate_limit_per_minute"])


class VirusTotalError(Exception):
    """Erro recuperável da API VirusTotal (5xx, timeout)."""


def get_virustotal_key() -> Optional[str]:
    key = os.getenv("VIRUSTOTAL_API_KEY")
    if not key:
        logger.warning("Variável VIRUSTOTAL_API_KEY não definida")
        logger.info("Configure com: export VIRUSTOTAL_API_KEY='sua_chave'")
    return key


@retry(max_attempts=3, base_delay=2.0, exceptions=(VirusTotalError,))
def _http_get_vt(file_hash: str, api_key: str) -> Optional[dict]:
    """Faz GET à API VT. Levanta VirusTotalError em 5xx ou timeout."""
    try:
        import requests
    except ImportError:
        logger.error("Módulo 'requests' não disponível. Instale com: pip install requests")
        return None

    url = f"{VIRUSTOTAL['api_url']}/files/{file_hash}"
    headers = {"x-apikey": api_key}
    timeout = VIRUSTOTAL["request_timeout_seconds"]

    _LIMITER.acquire()
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        raise VirusTotalError(f"Erro de rede: {exc}") from exc

    if response.status_code == 200:
        return response.json()
    if response.status_code == 404:
        logger.debug(f"Hash não encontrado no VirusTotal: {file_hash}")
        return None
    if response.status_code == 429:
        raise VirusTotalError("Rate limit do VirusTotal atingido (429)")
    if 500 <= response.status_code < 600:
        raise VirusTotalError(f"Erro servidor VT {response.status_code}")
    logger.warning(f"Erro VirusTotal (status {response.status_code}): {response.text[:200]}")
    return None


def fetch_vt_hash_info(
    file_hash: str,
    api_key: str,
    cache: Optional[VTCache] = None,
) -> Optional[dict]:
    """Procura no cache antes de bater na API. Cacheia resposta (200/404)."""
    if cache is not None:
        cached = cache.get(file_hash)
        if cached is not None:
            logger.debug(f"VT cache hit: {file_hash}")
            return cached if cached else None

    try:
        data = _http_get_vt(file_hash, api_key)
    except VirusTotalError as exc:
        logger.error(f"Falha após retries para {file_hash}: {exc}")
        return None

    if cache is not None:
        cache.set(file_hash, data if data is not None else {})

    return data


def is_malware(vt_data: dict) -> bool:
    try:
        attributes = vt_data.get("data", {}).get("attributes", {})
        stats = attributes.get("last_analysis_stats", {})
        return stats.get("malicious", 0) > 0
    except Exception:
        return False


def extract_malware_name(vt_data: dict) -> Optional[str]:
    try:
        attributes = vt_data.get("data", {}).get("attributes", {})
        results = attributes.get("last_analysis_results", {})

        for vendor, detection in results.items():
            if detection.get("category") == "malware":
                if detection.get("engine_name"):
                    return f"{vendor}:{detection.get('result', 'Unknown')}"

        if results:
            first_detection = next(iter(results.values()), {})
            return first_detection.get("result", "Unknown")
        return None
    except Exception:
        return None


def load_signatures(signature_file: Path) -> Dict[str, str]:
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


def update_single_hash(
    file_hash: str,
    signature_file: Path = PATHS["signatures"],
    cache: Optional[VTCache] = None,
) -> bool:
    api_key = get_virustotal_key()
    if not api_key:
        logger.error("API key do VirusTotal necessária")
        return False

    logger.info(f"Consultando VirusTotal para hash: {file_hash}")
    vt_data = fetch_vt_hash_info(file_hash, api_key, cache=cache)

    if not vt_data:
        logger.info(f"Sem dados para: {file_hash}")
        return False

    if is_malware(vt_data):
        malware_name = extract_malware_name(vt_data) or "Unknown"
        signatures = load_signatures(signature_file)
        signatures[file_hash] = malware_name
        logger.info(f"✓ Detectado como malware: {malware_name}")
        return save_signatures(signatures, signature_file)

    logger.info(f"Arquivo limpo (sem detecções): {file_hash}")
    return True


def batch_update(
    hashes: List[str],
    signature_file: Path = PATHS["signatures"],
    cache: Optional[VTCache] = None,
) -> int:
    """Consulta múltiplos hashes (com dedup). Retorna número adicionado."""
    api_key = get_virustotal_key()
    if not api_key:
        logger.error("API key do VirusTotal necessária")
        return 0

    signatures = load_signatures(signature_file)
    unique_hashes = [h for h in dict.fromkeys(hashes) if h not in signatures]

    if len(unique_hashes) < len(hashes):
        logger.info(
            f"Deduplicação: {len(hashes)} pedidos → {len(unique_hashes)} únicos novos"
        )

    added = 0
    for i, file_hash in enumerate(unique_hashes, 1):
        logger.info(f"[{i}/{len(unique_hashes)}] Consultando: {file_hash}")
        vt_data = fetch_vt_hash_info(file_hash, api_key, cache=cache)
        if vt_data and is_malware(vt_data):
            name = extract_malware_name(vt_data) or "Unknown"
            signatures[file_hash] = name
            added += 1
            logger.info(f"  ✓ Adicionado: {name}")

    if added > 0:
        save_signatures(signatures, signature_file)
        logger.info(f"Total adicionado: {added} assinatura(s)")

    return added


def main() -> None:
    logger.info("=== VirusTotal Signature Updater ===")
    api_key = get_virustotal_key()
    if not api_key:
        logger.error("VIRUSTOTAL_API_KEY não definida.")
        return
    logger.info(f"API key carregada (primeiros 8 caracteres: {api_key[:8]}...)")

    cache = VTCache(PATHS["vt_cache"], ttl_days=VIRUSTOTAL["cache_ttl_days"])
    try:
        choice = input("\n1. Consultar um hash\n2. Sair\nEscolha: ").strip()
        if choice == "1":
            file_hash = input("Hash SHA256: ").strip()
            if len(file_hash) == 64:
                update_single_hash(file_hash, cache=cache)
            else:
                logger.error("Hash SHA256 deve ter 64 caracteres")
        else:
            logger.info("Saindo...")
    finally:
        cache.close()


if __name__ == "__main__":
    main()
