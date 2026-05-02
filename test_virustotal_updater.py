"""
Unit tests para virustotal_updater (com requests mockado).
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import virustotal_updater as vt
from vt_cache import VTCache


def _malicious_response(name="Trojan.Test"):
    return {
        "data": {
            "attributes": {
                "last_analysis_stats": {"malicious": 5},
                "last_analysis_results": {
                    "Vendor1": {
                        "category": "malware",
                        "engine_name": "Vendor1",
                        "result": name,
                    }
                },
            }
        }
    }


def _clean_response():
    return {
        "data": {
            "attributes": {
                "last_analysis_stats": {"malicious": 0},
                "last_analysis_results": {},
            }
        }
    }


class TestIsMalware(unittest.TestCase):
    def test_detects_malicious(self):
        self.assertTrue(vt.is_malware(_malicious_response()))

    def test_clean_returns_false(self):
        self.assertFalse(vt.is_malware(_clean_response()))

    def test_malformed_returns_false(self):
        self.assertFalse(vt.is_malware({}))


class TestExtractMalwareName(unittest.TestCase):
    def test_extracts_named_detection(self):
        name = vt.extract_malware_name(_malicious_response("Generic.Trojan"))
        self.assertIn("Generic.Trojan", name)

    def test_returns_none_for_clean(self):
        self.assertIsNone(vt.extract_malware_name(_clean_response()))


class TestFetchVTHashInfo(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.cache = VTCache(Path(self.tmpdir.name) / "vt.db")

    def tearDown(self) -> None:
        self.cache.close()
        self.tmpdir.cleanup()

    def test_uses_cache_on_second_call(self):
        with mock.patch.object(vt, "_http_get_vt", return_value=_malicious_response()) as http:
            first = vt.fetch_vt_hash_info("h1", "key", cache=self.cache)
            second = vt.fetch_vt_hash_info("h1", "key", cache=self.cache)
            self.assertEqual(first, second)
            self.assertEqual(http.call_count, 1)

    def test_caches_404_to_avoid_requeries(self):
        with mock.patch.object(vt, "_http_get_vt", return_value=None) as http:
            vt.fetch_vt_hash_info("h2", "key", cache=self.cache)
            vt.fetch_vt_hash_info("h2", "key", cache=self.cache)
            self.assertEqual(http.call_count, 1)


class TestBatchUpdateDedup(unittest.TestCase):
    def test_dedup_skips_existing_signatures(self):
        with tempfile.TemporaryDirectory() as tmp:
            sigs = Path(tmp) / "sigs.json"
            sigs.write_text('{"malware_hashes": {"existing": "Old"}}')

            with mock.patch.object(vt, "get_virustotal_key", return_value="fakekey"), \
                 mock.patch.object(vt, "_http_get_vt", return_value=_malicious_response("New")):
                added = vt.batch_update(
                    ["existing", "new1", "new1", "new2"],
                    signature_file=sigs,
                    cache=None,
                )
                self.assertEqual(added, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
