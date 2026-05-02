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

    def test_path_normalization_slashes(self):
        m = ExclusionMatcher(["build/bin"])
        # Match com forward slashes (Unix)
        self.assertTrue(m.matches(Path("/project/build/bin/app.exe")))
        # Match com backslashes (Windows) - simulado via string normalization no matcher
        self.assertTrue(m.matches(Path("C:\\project\\build\\bin\\app.exe")))

    def test_absolute_path_pattern(self):
        m = ExclusionMatcher(["/usr/local/bin"])
        self.assertTrue(m.matches(Path("/usr/local/bin/python")))
        self.assertFalse(m.matches(Path("/home/user/usr/local/bin/extra")))

    def test_case_insensitivity(self):
        m = ExclusionMatcher(["NODE_MODULES"])
        self.assertTrue(m.matches(Path("/project/node_modules/index.js")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
