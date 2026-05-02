"""
Configuração centralizada do Anti-Virus Projeto.

Reúne paths, constantes e parâmetros de runtime num único lugar para evitar
duplicação e facilitar overrides em testes.
"""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

PATHS = {
    "signatures": PROJECT_ROOT / "signatures.json",
    "exclusions": PROJECT_ROOT / "exclusions.json",
    "schedule_config": PROJECT_ROOT / "schedule_config.json",
    "scan_cache": PROJECT_ROOT / ".scan_cache.db",
    "vt_cache": PROJECT_ROOT / ".vt_cache.db",
    "scan_history": PROJECT_ROOT / ".scan_history.db",
    "user_prefs": PROJECT_ROOT / ".user_prefs.json",
    "log_file": PROJECT_ROOT / "scan.log",
    "output_dir": PROJECT_ROOT / "output",
    "quarantine_dir": PROJECT_ROOT / "quarantine",
}

SCAN = {
    "buffer_size": 1024 * 1024,
    "file_timeout_seconds": 5.0,
    "max_file_size_bytes": 500 * 1024 * 1024,
    "cache_enabled": True,
}

VIRUSTOTAL = {
    "api_url": "https://www.virustotal.com/api/v3",
    "rate_limit_per_minute": 4,
    "cache_ttl_days": 30,
    "request_timeout_seconds": 30,
}

LOG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
}
