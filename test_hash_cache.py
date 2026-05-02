"""
Unit tests para hash_cache.HashCache.
"""
from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path

from hash_cache import HashCache


class HashCacheTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "cache.db"
        self.cache = HashCache(self.db_path)
        self.sample = Path(self.tmpdir.name) / "sample.bin"
        self.sample.write_bytes(b"hello world")

    def tearDown(self) -> None:
        self.cache.close()
        self.tmpdir.cleanup()


class TestHashCacheBasic(HashCacheTestBase):
    def test_get_returns_none_when_empty(self):
        self.assertIsNone(self.cache.get(self.sample))

    def test_set_then_get_returns_hash(self):
        self.cache.set(self.sample, "abc123")
        self.assertEqual(self.cache.get(self.sample), "abc123")

    def test_set_overwrites_previous_hash(self):
        self.cache.set(self.sample, "first")
        self.cache.set(self.sample, "second")
        self.assertEqual(self.cache.get(self.sample), "second")


class TestHashCacheInvalidation(HashCacheTestBase):
    def test_invalidates_when_size_changes(self):
        self.cache.set(self.sample, "abc")
        self.sample.write_bytes(b"different content here")
        self.assertIsNone(self.cache.get(self.sample))

    def test_invalidates_when_mtime_changes(self):
        self.cache.set(self.sample, "abc")
        future = time.time() + 10
        os.utime(self.sample, (future, future))
        self.assertIsNone(self.cache.get(self.sample))

    def test_explicit_invalidate_removes_entry(self):
        self.cache.set(self.sample, "abc")
        self.cache.invalidate(self.sample)
        self.assertIsNone(self.cache.get(self.sample))


class TestHashCacheEdgeCases(HashCacheTestBase):
    def test_get_nonexistent_file_returns_none(self):
        missing = Path(self.tmpdir.name) / "missing.bin"
        self.assertIsNone(self.cache.get(missing))

    def test_set_nonexistent_file_does_not_raise(self):
        missing = Path(self.tmpdir.name) / "missing.bin"
        self.cache.set(missing, "abc")
        self.assertIsNone(self.cache.get(missing))

    def test_clear_empties_cache(self):
        self.cache.set(self.sample, "abc")
        self.cache.clear()
        self.assertIsNone(self.cache.get(self.sample))
        self.assertEqual(self.cache.stats()["entries"], 0)

    def test_stats_reports_entries(self):
        self.cache.set(self.sample, "abc")
        stats = self.cache.stats()
        self.assertEqual(stats["entries"], 1)
        self.assertGreater(stats["db_size_bytes"], 0)


class TestHashCachePersistence(unittest.TestCase):
    def test_cache_persists_across_instances(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "cache.db"
            sample = Path(tmp) / "sample.bin"
            sample.write_bytes(b"persistent content")

            first = HashCache(db_path)
            first.set(sample, "persisted_hash")
            first.close()

            second = HashCache(db_path)
            try:
                self.assertEqual(second.get(sample), "persisted_hash")
            finally:
                second.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
