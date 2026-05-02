"""Testes para ``gui_filters`` — pura, sem GUI."""
from __future__ import annotations

import unittest

from Virus_project import ScanResult
from gui_filters import FilterCriteria, filter_results, format_elapsed, format_eta


def _results():
    return [
        ScanResult(file_path="/x/clean.txt", status="clean", sha256="a" * 64),
        ScanResult(file_path="/x/another.log", status="clean", sha256="b" * 64),
        ScanResult(
            file_path="/x/bad/evil.exe",
            status="infected",
            reason="Trojan",
            sha256="c" * 64,
        ),
        ScanResult(file_path="/x/skip.dat", status="skip", reason="?"),
    ]


class TestFilterResults(unittest.TestCase):
    def test_default_returns_everything(self):
        out = filter_results(_results(), FilterCriteria())
        self.assertEqual(len(out), 4)

    def test_only_infected(self):
        crit = FilterCriteria(show_clean=False, show_skipped=False)
        out = filter_results(_results(), crit)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].status, "infected")

    def test_search_substring_case_insensitive(self):
        crit = FilterCriteria(query="EVIL")
        out = filter_results(_results(), crit)
        self.assertEqual(len(out), 1)
        self.assertIn("evil", out[0].file_path)

    def test_search_with_empty_query_includes_all(self):
        crit = FilterCriteria(query="   ")
        out = filter_results(_results(), crit)
        self.assertEqual(len(out), 4)

    def test_sort_by_status_puts_infected_first(self):
        out = filter_results(_results(), FilterCriteria())
        self.assertEqual(out[0].status, "infected")

    def test_sort_by_name(self):
        out = filter_results(_results(), FilterCriteria(sort_by="name"))
        names = [r.file_path.rsplit("/", 1)[-1] for r in out]
        self.assertEqual(names, sorted(names, key=str.lower))


class TestFormatHelpers(unittest.TestCase):
    def test_eta_zero_rate(self):
        self.assertEqual(format_eta(100, 0), "—")

    def test_eta_zero_remaining(self):
        self.assertEqual(format_eta(0, 10), "—")

    def test_eta_normal(self):
        self.assertEqual(format_eta(120, 10), "00:12")

    def test_eta_minutes(self):
        self.assertEqual(format_eta(600, 5), "02:00")

    def test_eta_hours(self):
        out = format_eta(36000, 1)
        self.assertTrue(out.startswith("10h"))

    def test_elapsed_seconds(self):
        self.assertEqual(format_elapsed(45), "00:45")

    def test_elapsed_minutes(self):
        self.assertEqual(format_elapsed(125), "02:05")

    def test_elapsed_negative_clamped(self):
        self.assertEqual(format_elapsed(-5), "00:00")


if __name__ == "__main__":
    unittest.main(verbosity=2)
