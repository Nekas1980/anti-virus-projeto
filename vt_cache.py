"""
Cache SQLite para respostas da API VirusTotal.

Evita re-querer o mesmo hash se já o consultámos recentemente. Cada entrada
expira após `ttl_days` (default 30, configurável em `config.VIRUSTOTAL`).
"""
from __future__ import annotations

import json
import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS vt_cache (
    file_hash TEXT PRIMARY KEY,
    response_json TEXT NOT NULL,
    cached_at REAL NOT NULL,
    expires_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_vt_expires ON vt_cache(expires_at);
"""


class VTCache:
    """Cache persistente de respostas VirusTotal com TTL."""

    def __init__(self, db_path: Path, ttl_days: int = 30):
        self.db_path = db_path
        self.ttl_seconds = ttl_days * 86400
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            isolation_level=None,
        )
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(_SCHEMA)

    def get(self, file_hash: str) -> Optional[dict]:
        """Devolve a resposta cacheada se existir e não tiver expirado."""
        now = time.time()
        with self._lock:
            row = self._conn.execute(
                "SELECT response_json, expires_at FROM vt_cache WHERE file_hash = ?",
                (file_hash,),
            ).fetchone()

        if row is None:
            return None

        response_json, expires_at = row
        if expires_at < now:
            self.invalidate(file_hash)
            return None

        try:
            return json.loads(response_json)
        except json.JSONDecodeError:
            logger.warning(f"Cache VT corrompido para {file_hash}, invalidando")
            self.invalidate(file_hash)
            return None

    def set(self, file_hash: str, response: dict) -> None:
        """Armazena resposta no cache. `None` é codificado como entrada vazia para evitar requeries."""
        now = time.time()
        payload = json.dumps(response, ensure_ascii=False)
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO vt_cache (file_hash, response_json, cached_at, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(file_hash) DO UPDATE SET
                    response_json = excluded.response_json,
                    cached_at = excluded.cached_at,
                    expires_at = excluded.expires_at
                """,
                (file_hash, payload, now, now + self.ttl_seconds),
            )

    def invalidate(self, file_hash: str) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM vt_cache WHERE file_hash = ?", (file_hash,))

    def purge_expired(self) -> int:
        """Remove entradas expiradas. Devolve número de linhas removidas."""
        now = time.time()
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM vt_cache WHERE expires_at < ?", (now,)
            )
            return cur.rowcount

    def stats(self) -> dict:
        with self._lock:
            total = self._conn.execute("SELECT COUNT(*) FROM vt_cache").fetchone()[0]
            expired = self._conn.execute(
                "SELECT COUNT(*) FROM vt_cache WHERE expires_at < ?", (time.time(),)
            ).fetchone()[0]
        return {"entries": total, "expired": expired}

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def __enter__(self) -> "VTCache":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
