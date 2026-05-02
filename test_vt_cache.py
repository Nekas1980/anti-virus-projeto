"""
Unit tests para vt_cache.VTCache.
"""
from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from vt_cache import VTCache


class VTCacheTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db = Path(self.tmpdir.name) / "vt.db"
        self.cache = VTCache(self.db, ttl_days=30)

    def tearDown(self) -> None:
        self.cache.close()
        self.tmpdir.cleanup()


class TestVTCacheBasic(VTCacheTestBase):
    def test_get_returns_none_when_empty(self):
        self.assertIsNone(self.cache.get("abc"))

    def test_set_and_get_roundtrip(self):
        payload = {"data": {"attributes": {"last_analysis_stats": {"malicious": 5}}}}
        self.cache.set("hash1", payload)
        self.assertEqual(self.cache.get("hash1"), payload)

    def test_empty_dict_is_distinguishable_from_miss(self):
        self.cache.set("hash1", {})
        self.assertEqual(self.cache.get("hash1"), {})


class TestVTCacheExpiry(unittest.TestCase):
    def test_expired_entry_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = VTCache(Path(tmp) / "vt.db", ttl_days=30)
            try:
                with mock.patch("vt_cache.time.time") as mock_time:
                    mock_time.return_value = 1000.0
                    cache.set("h", {"x": 1})
                    mock_time.return_value = 1000.0 + (31 * 86400)
                    self.assertIsNone(cache.get("h"))
            finally:
                cache.close()

    def test_purge_expired_removes_old(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = VTCache(Path(tmp) / "vt.db", ttl_days=30)
            try:
                with mock.patch("vt_cache.time.time") as mock_time:
                    mock_time.return_value = 1000.0
                    cache.set("a", {"x": 1})
                    cache.set("b", {"x": 2})
                    mock_time.return_value = 1000.0 + (31 * 86400)
                    removed = cache.purge_expired()
                    self.assertEqual(removed, 2)
            finally:
                cache.close()


class TestVTCacheStats(VTCacheTestBase):
    def test_stats_reports_counts(self):
        self.cache.set("a", {"x": 1})
        self.cache.set("b", {"x": 2})
        stats = self.cache.stats()
        self.assertEqual(stats["entries"], 2)
        self.assertEqual(stats["expired"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
