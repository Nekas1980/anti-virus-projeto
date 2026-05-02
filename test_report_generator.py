"""Testes para o gerador de relatórios HTML/JSON refactored na Fase 3."""
from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path

from Virus_project import ScanResult
from report_generator import (
    HTMLReportGenerator,
    ReportMetadata,
    _classify_risk,
    _format_duration,
    _top_infected_dirs,
    _truncate,
    generate_json_report,
)


def _sample_results():
    return [
        ScanResult(file_path="/tmp/a.txt", status="clean", sha256="a" * 64),
        ScanResult(file_path="/tmp/b.txt", status="clean", sha256="b" * 64),
        ScanResult(
            file_path="/tmp/bad/evil.exe",
            status="infected",
            reason="Trojan.Test",
            sha256="c" * 64,
        ),
        ScanResult(
            file_path="/tmp/bad/worm.bin",
            status="infected",
            reason="Worm",
            sha256="d" * 64,
        ),
        ScanResult(file_path="/tmp/skip", status="skip", reason="não é ficheiro"),
    ]


class TestReportMetadata(unittest.TestCase):
    def test_duration_uses_finished_at(self):
        meta = ReportMetadata(started_at=100.0, finished_at=103.5)
        self.assertAlmostEqual(meta.duration_seconds, 3.5, places=3)

    def test_duration_falls_back_to_now(self):
        meta = ReportMetadata(started_at=time.time() - 0.05)
        self.assertGreaterEqual(meta.duration_seconds, 0.0)

    def test_scan_rate_zero_division_safe(self):
        meta = ReportMetadata(started_at=100.0, finished_at=100.0)
        self.assertEqual(meta.scan_rate(10), 0.0)

    def test_scan_rate_normal(self):
        meta = ReportMetadata(started_at=100.0, finished_at=110.0)
        self.assertAlmostEqual(meta.scan_rate(50), 5.0)

    def test_to_dict_roundtrip(self):
        meta = ReportMetadata(
            scan_id="abc", started_at=100.0, finished_at=102.0, paths=["/x"]
        )
        d = meta.to_dict()
        self.assertEqual(d["scan_id"], "abc")
        self.assertEqual(d["paths"], ["/x"])
        self.assertEqual(d["duration_seconds"], 2.0)


class TestRiskClassification(unittest.TestCase):
    def test_no_data(self):
        label, css, _ = _classify_risk(0, 0)
        self.assertEqual(label, "SEM DADOS")
        self.assertEqual(css, "warn")

    def test_safe(self):
        label, css, _ = _classify_risk(0, 100)
        self.assertEqual(label, "SEGURO")
        self.assertEqual(css, "safe")

    def test_warn_low_count(self):
        label, css, _ = _classify_risk(2, 100)
        self.assertEqual(label, "ATENÇÃO")
        self.assertEqual(css, "warn")

    def test_danger_high_count(self):
        label, css, _ = _classify_risk(20, 100)
        self.assertEqual(label, "RISCO ELEVADO")
        self.assertEqual(css, "danger")


class TestHelpers(unittest.TestCase):
    def test_format_duration_milliseconds(self):
        self.assertIn("ms", _format_duration(0.5))

    def test_format_duration_seconds(self):
        self.assertIn("s", _format_duration(12.3))

    def test_format_duration_minutes(self):
        self.assertIn("m", _format_duration(125))

    def test_truncate_short(self):
        self.assertEqual(_truncate("abc", 10), "abc")

    def test_truncate_long(self):
        out = _truncate("a" * 50, 10)
        self.assertEqual(len(out), 10)
        self.assertTrue(out.endswith("…"))

    def test_top_infected_dirs(self):
        results = _sample_results()
        top = _top_infected_dirs(results)
        self.assertEqual(top[0][0], "/tmp/bad")
        self.assertEqual(top[0][1], 2)


class TestHTMLReport(unittest.TestCase):
    def test_generate_html_has_metadata_and_charts(self):
        results = _sample_results()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r.html"
            meta = ReportMetadata(
                started_at=time.time() - 5,
                finished_at=time.time(),
                paths=["/tmp/a", "/tmp/bad"],
            )
            ok = HTMLReportGenerator.generate(results, out, metadata=meta)
            self.assertTrue(ok)
            html = out.read_text(encoding="utf-8")
            self.assertIn("Trojan.Test", html)
            self.assertIn("STATUS_DATA", html)
            self.assertIn("DIRS_DATA", html)
            self.assertIn("Resumo Executivo", html)
            self.assertIn("ATENÇÃO", html)
            self.assertIn("/tmp/a", html)

    def test_safe_when_no_infected(self):
        results = [
            ScanResult(file_path="/x", status="clean", sha256="a" * 64),
            ScanResult(file_path="/y", status="clean", sha256="b" * 64),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r.html"
            ok = HTMLReportGenerator.generate(results, out)
            self.assertTrue(ok)
            html = out.read_text(encoding="utf-8")
            self.assertIn("SEGURO", html)

    def test_handles_empty_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r.html"
            ok = HTMLReportGenerator.generate([], out)
            self.assertTrue(ok)


class TestJSONReport(unittest.TestCase):
    def test_legacy_no_metadata_returns_list(self):
        results = _sample_results()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r.json"
            ok = generate_json_report(results, out)
            self.assertTrue(ok)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 5)

    def test_with_metadata_includes_envelope(self):
        results = _sample_results()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r.json"
            meta = ReportMetadata(scan_id="test-id", paths=["/tmp"])
            ok = generate_json_report(results, out, metadata=meta)
            self.assertTrue(ok)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertIn("metadata", data)
            self.assertIn("counts", data)
            self.assertIn("results", data)
            self.assertEqual(data["metadata"]["scan_id"], "test-id")
            self.assertEqual(data["counts"]["infected"], 2)
            self.assertEqual(data["counts"]["clean"], 2)
            self.assertEqual(data["counts"]["skipped"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
