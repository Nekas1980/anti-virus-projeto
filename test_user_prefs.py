"""
Unit tests para user_prefs.UserPrefs.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from user_prefs import UserPrefs


class TestUserPrefs(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tmpdir.name) / "prefs.json"

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_defaults_when_no_file(self):
        prefs = UserPrefs(self.path)
        self.assertEqual(prefs.recent_paths, [])
        self.assertTrue(prefs.get("notify_on_complete"))

    def test_set_persists_across_instances(self):
        prefs = UserPrefs(self.path)
        prefs.set("notify_on_complete", False)

        reloaded = UserPrefs(self.path)
        self.assertFalse(reloaded.get("notify_on_complete"))

    def test_add_recent_dedups_and_orders(self):
        prefs = UserPrefs(self.path)
        prefs.add_recent_path("/a")
        prefs.add_recent_path("/b")
        prefs.add_recent_path("/a")
        self.assertEqual(prefs.recent_paths, ["/a", "/b"])

    def test_add_recent_caps_at_max(self):
        prefs = UserPrefs(self.path)
        prefs.set("max_recent", 3)
        for p in ["/a", "/b", "/c", "/d", "/e"]:
            prefs.add_recent_path(p)
        self.assertEqual(prefs.recent_paths, ["/e", "/d", "/c"])

    def test_corrupt_file_falls_back_to_defaults(self):
        self.path.write_text("not valid json", encoding="utf-8")
        prefs = UserPrefs(self.path)
        self.assertEqual(prefs.recent_paths, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
