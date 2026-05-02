"""
Cache local em SQLite para hashes SHA-256.

Evita recomputar o hash de ficheiros já analisados anteriormente. A entrada é
invalidada se o tamanho ou mtime do ficheiro mudou desde o último cálculo.

A conexão SQLite usa WAL para permitir leituras concorrentes durante uma
varredura multi-thread. Escritas são serializadas com um lock para
robustez quando vários scans usam a mesma instância.
"""
from __future__ import annotations

import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS hash_cache (
    file_path TEXT PRIMARY KEY,
    file_size INTEGER NOT NULL,
    mtime REAL NOT NULL,
    sha256 TEXT NOT NULL,
    cached_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cached_at ON hash_cache(cached_at);
"""


class HashCache:
    """Cache persistente de hashes SHA-256 baseado em (path, size, mtime)."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            isolation_level=None,
        )
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.executescript(_SCHEMA)

    def get(self, file_path: Path) -> Optional[str]:
        """Devolve o SHA-256 cacheado ou None se não existe ou está desactualizado."""
        try:
            stat = file_path.stat()
        except OSError:
            return None

        key = self._key(file_path)
        with self._lock:
            row = self._conn.execute(
                "SELECT file_size, mtime, sha256 FROM hash_cache WHERE file_path = ?",
                (key,),
            ).fetchone()

        if row is None:
            return None

        cached_size, cached_mtime, cached_sha = row
        if cached_size != stat.st_size or cached_mtime != stat.st_mtime:
            return None
        return cached_sha

    def set(self, file_path: Path, sha256: str) -> None:
        """Armazena o hash de um ficheiro com o size/mtime actuais."""
        try:
            stat = file_path.stat()
        except OSError:
            return

        key = self._key(file_path)
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO hash_cache (file_path, file_size, mtime, sha256, cached_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    file_size = excluded.file_size,
                    mtime = excluded.mtime,
                    sha256 = excluded.sha256,
                    cached_at = excluded.cached_at
                """,
                (key, stat.st_size, stat.st_mtime, sha256, time.time()),
            )

    def invalidate(self, file_path: Path) -> None:
        """Remove a entrada de cache para um ficheiro."""
        with self._lock:
            self._conn.execute(
                "DELETE FROM hash_cache WHERE file_path = ?",
                (self._key(file_path),),
            )

    def stats(self) -> dict:
        """Devolve métricas do cache (entradas, tamanho do ficheiro)."""
        with self._lock:
            total = self._conn.execute(
                "SELECT COUNT(*) FROM hash_cache"
            ).fetchone()[0]
        size_bytes = self.db_path.stat().st_size if self.db_path.exists() else 0
        return {"entries": total, "db_size_bytes": size_bytes}

    def clear(self) -> None:
        """Remove todas as entradas do cache."""
        with self._lock:
            self._conn.execute("DELETE FROM hash_cache")

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def __enter__(self) -> "HashCache":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @staticmethod
    def _key(file_path: Path) -> str:
        try:
            return str(file_path.resolve())
        except OSError:
            return str(file_path)
