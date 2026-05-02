"""
Unit tests para scan_history.ScanHistory.
"""
from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from scan_history import ScanHistory


class TestScanHistory(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db = Path(self.tmpdir.name) / "history.db"
        self.history = ScanHistory(self.db)

    def tearDown(self) -> None:
        self.history.close()
        self.tmpdir.cleanup()

    def test_record_creates_entry(self):
        rec = self.history.record(
            paths=["/tmp/a"],
            total=10,
            clean=8,
            infected=1,
            skipped=1,
            started_at=time.time() - 5,
        )
        self.assertEqual(rec.total, 10)
        self.assertGreater(rec.duration_seconds, 0)
        self.assertTrue(rec.scan_id)

    def test_recent_orders_newest_first(self):
        now = time.time()
        self.history.record(paths=["/a"], total=1, clean=1, infected=0, skipped=0, started_at=now - 100)
        self.history.record(paths=["/b"], total=2, clean=2, infected=0, skipped=0, started_at=now - 10)
        recent = self.history.recent(limit=10)
        self.assertEqual(recent[0].paths, ["/b"])
        self.assertEqual(recent[1].paths, ["/a"])

    def test_get_by_id_returns_record(self):
        rec = self.history.record(
            paths=["/x"], total=1, clean=1, infected=0, skipped=0, started_at=time.time()
        )
        fetched = self.history.get(rec.scan_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.scan_id, rec.scan_id)

    def test_delete_removes_record(self):
        rec = self.history.record(
            paths=["/x"], total=1, clean=1, infected=0, skipped=0, started_at=time.time()
        )
        self.assertTrue(self.history.delete(rec.scan_id))
        self.assertIsNone(self.history.get(rec.scan_id))

    def test_paths_are_serialized_as_strings(self):
        rec = self.history.record(
            paths=[Path("/some/dir"), "/other"],
            total=0,
            clean=0,
            infected=0,
            skipped=0,
            started_at=time.time(),
        )
        fetched = self.history.get(rec.scan_id)
        self.assertEqual(fetched.paths, ["/some/dir", "/other"])

    def test_clear_empties_history(self):
        self.history.record(
            paths=["/a"], total=1, clean=1, infected=0, skipped=0, started_at=time.time()
        )
        self.history.clear()
        self.assertEqual(self.history.recent(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
