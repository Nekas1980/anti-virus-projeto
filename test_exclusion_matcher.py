"""
Unit tests para exclusion_matcher.ExclusionMatcher.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from exclusion_matcher import ExclusionMatcher


class TestExclusionMatcher(unittest.TestCase):
    def test_matches_directory_pattern(self):
        m = ExclusionMatcher(["node_modules", ".git"])
        self.assertTrue(m.matches(Path("/project/node_modules/lodash/index.js")))
        self.assertTrue(m.matches(Path("/project/.git/HEAD")))

    def test_does_not_match_unrelated_path(self):
        m = ExclusionMatcher(["node_modules", ".git"])
        self.assertFalse(m.matches(Path("/project/src/main.py")))

    def test_matches_exact_basename(self):
        m = ExclusionMatcher([".env", ".DS_Store"])
        self.assertTrue(m.matches(Path("/project/.env")))
        self.assertTrue(m.matches(Path("/some/dir/.DS_Store")))

    def test_matches_glob_extension(self):
        m = ExclusionMatcher(["*.tmp", "*.egg-info"])
        self.assertTrue(m.matches(Path("/tmp/foo.tmp")))
        self.assertTrue(m.matches(Path("/proj/pkg.egg-info")))

    def test_empty_patterns_never_matches(self):
        m = ExclusionMatcher([])
        self.assertFalse(m.matches(Path("/anywhere")))
        self.assertEqual(len(m), 0)

    def test_patterns_property_preserves_input(self):
        patterns = ["a", "b", "c"]
        m = ExclusionMatcher(patterns)
        self.assertEqual(m.patterns, patterns)


if __name__ == "__main__":
    unittest.main(verbosity=2)
