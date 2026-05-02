"""
Persistência do histórico de varreduras.

Cada scan grava uma linha em SQLite com totais e duração — alimenta a vista
de histórico na GUI e permite analytics simples sem reler reports JSON.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Sequence

_SCHEMA = """
CREATE TABLE IF NOT EXISTS scan_history (
    scan_id TEXT PRIMARY KEY,
    started_at REAL NOT NULL,
    finished_at REAL NOT NULL,
    duration_seconds REAL NOT NULL,
    paths_json TEXT NOT NULL,
    total INTEGER NOT NULL,
    clean INTEGER NOT NULL,
    infected INTEGER NOT NULL,
    skipped INTEGER NOT NULL,
    report_path TEXT
);
CREATE INDEX IF NOT EXISTS idx_history_started ON scan_history(started_at DESC);
"""


@dataclass
class ScanRecord:
    scan_id: str
    started_at: float
    finished_at: float
    duration_seconds: float
    paths: List[str]
    total: int
    clean: int
    infected: int
    skipped: int
    report_path: Optional[str] = None

    @property
    def started_iso(self) -> str:
        return datetime.fromtimestamp(self.started_at).isoformat(timespec="seconds")


class ScanHistory:
    """Histórico persistente de varreduras."""

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
        self._conn.executescript(_SCHEMA)

    def record(
        self,
        paths: Sequence[Path | str],
        total: int,
        clean: int,
        infected: int,
        skipped: int,
        started_at: float,
        finished_at: Optional[float] = None,
        report_path: Optional[Path] = None,
    ) -> ScanRecord:
        end = finished_at if finished_at is not None else time.time()
        record = ScanRecord(
            scan_id=str(uuid.uuid4()),
            started_at=started_at,
            finished_at=end,
            duration_seconds=max(0.0, end - started_at),
            paths=[str(p) for p in paths],
            total=total,
            clean=clean,
            infected=infected,
            skipped=skipped,
            report_path=str(report_path) if report_path else None,
        )
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO scan_history
                    (scan_id, started_at, finished_at, duration_seconds,
                     paths_json, total, clean, infected, skipped, report_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.scan_id,
                    record.started_at,
                    record.finished_at,
                    record.duration_seconds,
                    json.dumps(record.paths, ensure_ascii=False),
                    record.total,
                    record.clean,
                    record.infected,
                    record.skipped,
                    record.report_path,
                ),
            )
        return record

    def recent(self, limit: int = 50) -> List[ScanRecord]:
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT scan_id, started_at, finished_at, duration_seconds, paths_json,
                       total, clean, infected, skipped, report_path
                FROM scan_history
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def get(self, scan_id: str) -> Optional[ScanRecord]:
        with self._lock:
            row = self._conn.execute(
                """
                SELECT scan_id, started_at, finished_at, duration_seconds, paths_json,
                       total, clean, infected, skipped, report_path
                FROM scan_history WHERE scan_id = ?
                """,
                (scan_id,),
            ).fetchone()
        return self._row_to_record(row) if row else None

    def delete(self, scan_id: str) -> bool:
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM scan_history WHERE scan_id = ?", (scan_id,)
            )
            return cur.rowcount > 0

    def clear(self) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM scan_history")

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def __enter__(self) -> "ScanHistory":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @staticmethod
    def _row_to_record(row: tuple) -> ScanRecord:
        return ScanRecord(
            scan_id=row[0],
            started_at=row[1],
            finished_at=row[2],
            duration_seconds=row[3],
            paths=json.loads(row[4]),
            total=row[5],
            clean=row[6],
            infected=row[7],
            skipped=row[8],
            report_path=row[9],
        )
