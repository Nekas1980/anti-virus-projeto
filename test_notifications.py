"""Tests for notifications.py — plyer calls are always mocked."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import ANY, MagicMock, patch

from notifications import notify, notify_scan_complete, notify_scan_started


class TestNotifyImportError(unittest.TestCase):
    """Covers the ImportError branch when plyer is absent."""

    def test_returns_false_when_plyer_missing(self):
        with patch.dict(sys.modules, {"plyer": None}):
            result = notify("T", "M")
        self.assertFalse(result)

    def test_debug_logged_when_plyer_missing(self):
        with patch.dict(sys.modules, {"plyer": None}):
            with patch("notifications.logger") as mock_log:
                notify("title", "msg")
            mock_log.debug.assert_called_once()


class TestNotifySuccess(unittest.TestCase):
    """Covers the happy-path branch when plyer is present."""

    def _mock_plyer(self):
        m = MagicMock()
        return m

    def test_returns_true_when_notify_succeeds(self):
        mock_plyer = self._mock_plyer()
        with patch.dict(sys.modules, {"plyer": mock_plyer}):
            result = notify("title", "message", timeout=5)
        self.assertTrue(result)
        mock_plyer.notification.notify.assert_called_once_with(
            title="title",
            message="message",
            app_name=ANY,
            timeout=5,
        )

    def test_returns_false_when_notify_raises(self):
        mock_plyer = self._mock_plyer()
        mock_plyer.notification.notify.side_effect = RuntimeError("backend error")
        with patch.dict(sys.modules, {"plyer": mock_plyer}):
            result = notify("title", "message")
        self.assertFalse(result)

    def test_warning_logged_when_notify_raises(self):
        mock_plyer = self._mock_plyer()
        mock_plyer.notification.notify.side_effect = Exception("boom")
        with patch.dict(sys.modules, {"plyer": mock_plyer}):
            with patch("notifications.logger") as mock_log:
                notify("title", "message")
            mock_log.warning.assert_called_once()


class TestNotifyScanComplete(unittest.TestCase):
    """Covers both branches of notify_scan_complete()."""

    def test_infected_title_contains_count(self):
        with patch("notifications.notify", return_value=True) as mock_n:
            result = notify_scan_complete(3, 10, 2)
        self.assertTrue(result)
        title, _message = mock_n.call_args[0]
        self.assertIn("3", title)

    def test_clean_title_when_no_infected(self):
        with patch("notifications.notify", return_value=True) as mock_n:
            result = notify_scan_complete(0, 5)
        self.assertTrue(result)
        title, _message = mock_n.call_args[0]
        self.assertNotIn("detectada", title)

    def test_propagates_notify_return_value(self):
        with patch("notifications.notify", return_value=False):
            self.assertFalse(notify_scan_complete(1, 0))


class TestNotifyScanStarted(unittest.TestCase):
    """Covers notify_scan_started()."""

    def test_calls_notify_with_path_count(self):
        with patch("notifications.notify", return_value=True) as mock_n:
            result = notify_scan_started(4)
        self.assertTrue(result)
        mock_n.assert_called_once()
        _title, message = mock_n.call_args[0]
        self.assertIn("4", message)

    def test_propagates_notify_return_value(self):
        with patch("notifications.notify", return_value=False):
            self.assertFalse(notify_scan_started(1))


if __name__ == "__main__":
    unittest.main()
