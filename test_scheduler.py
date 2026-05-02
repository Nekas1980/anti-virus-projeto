"""Testes para ``scheduler.py`` (Fase 4 / 4.1)."""
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

from scheduler import ScanScheduler
from Virus_project import ScanResult


class TestSchedulerConfig(unittest.TestCase):
    def test_default_config_has_intervals(self):
        sched = ScanScheduler.__new__(ScanScheduler)
        cfg = sched._get_default_config()
        self.assertTrue(cfg["enabled"])
        self.assertGreater(len(cfg["intervals"]), 0)
        first = cfg["intervals"][0]
        self.assertIn("hour", first)
        self.assertIn("paths", first)

    def test_load_config_returns_default_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "missing.json"
            with mock.patch("scheduler.signal.signal"):
                with mock.patch("scheduler.HashCache"):
                    with mock.patch("scheduler.ScanHistory"):
                        sched = ScanScheduler(config_file=cfg_path)
            self.assertTrue(sched.config["enabled"])

    def test_load_config_returns_default_on_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "bad.json"
            cfg_path.write_text("{not valid json")
            with mock.patch("scheduler.signal.signal"):
                with mock.patch("scheduler.HashCache"):
                    with mock.patch("scheduler.ScanHistory"):
                        sched = ScanScheduler(config_file=cfg_path)
            self.assertTrue(sched.config["enabled"])

    def test_create_schedule_config_writes_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "schedule.json"
            ok = ScanScheduler.create_schedule_config(target)
            self.assertTrue(ok)
            self.assertTrue(target.exists())
            data = json.loads(target.read_text(encoding="utf-8"))
            self.assertIn("intervals", data)


class TestShouldRunNow(unittest.TestCase):
    def _make_sched(self):
        with mock.patch("scheduler.signal.signal"):
            with mock.patch("scheduler.HashCache"):
                with mock.patch("scheduler.ScanHistory"):
                    sched = ScanScheduler.__new__(ScanScheduler)
                    sched.config = sched._get_default_config()
                    sched.config_file = Path("/tmp/x")
                    return sched

    def test_runs_at_matching_time_and_day(self):
        sched = self._make_sched()
        fake_now = datetime(2026, 5, 4, 9, 0, 30)  # Mon 09:00:30
        interval = {"hour": 9, "minute": 0, "days": ["Mon"]}
        with mock.patch("scheduler.datetime") as dt:
            dt.now.return_value = fake_now
            dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            self.assertTrue(sched._should_run_now(interval))

    def test_skips_on_wrong_day(self):
        sched = self._make_sched()
        fake_now = datetime(2026, 5, 3, 9, 0, 30)  # Sunday
        interval = {"hour": 9, "minute": 0, "days": ["Mon", "Tue"]}
        with mock.patch("scheduler.datetime") as dt:
            dt.now.return_value = fake_now
            dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            self.assertFalse(sched._should_run_now(interval))

    def test_skips_outside_one_minute_window(self):
        sched = self._make_sched()
        fake_now = datetime(2026, 5, 4, 9, 5, 0)
        interval = {"hour": 9, "minute": 0, "days": ["Mon"]}
        with mock.patch("scheduler.datetime") as dt:
            dt.now.return_value = fake_now
            dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            self.assertFalse(sched._should_run_now(interval))

    def test_runs_when_no_days_specified(self):
        sched = self._make_sched()
        fake_now = datetime(2026, 5, 4, 9, 0, 0)
        interval = {"hour": 9, "minute": 0}
        with mock.patch("scheduler.datetime") as dt:
            dt.now.return_value = fake_now
            dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            self.assertTrue(sched._should_run_now(interval))


class TestRunScan(unittest.TestCase):
    def _make_sched_with_mocks(self, tmp_dir: Path):
        with mock.patch("scheduler.signal.signal"):
            with mock.patch("scheduler.HashCache") as cache_cls:
                with mock.patch("scheduler.ScanHistory") as hist_cls:
                    cache_cls.return_value = mock.MagicMock()
                    hist_cls.return_value = mock.MagicMock()
                    sched = ScanScheduler(config_file=tmp_dir / "schedule.json")
        return sched

    def test_run_scan_skips_when_no_valid_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sched = self._make_sched_with_mocks(tmp_path)
            interval = {"name": "test", "paths": ["/nonexistent/xyz/abc"]}
            with mock.patch("scheduler.scan_directory") as scan:
                sched._run_scan(interval)
                scan.assert_not_called()

    def test_run_scan_records_history_and_saves_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            scan_target = tmp_path / "scan_me"
            scan_target.mkdir()
            (scan_target / "f.txt").write_text("hello")

            sched = self._make_sched_with_mocks(tmp_path)
            results = [
                ScanResult(file_path=str(scan_target / "f.txt"), status="clean", sha256="a" * 64),
                ScanResult(
                    file_path=str(scan_target / "evil"),
                    status="infected",
                    reason="Trojan",
                    sha256="b" * 64,
                ),
            ]
            interval = {
                "name": "test",
                "paths": [str(scan_target)],
                "report_dir": str(tmp_path / "reports"),
            }

            with mock.patch("scheduler.scan_directory", return_value=results):
                with mock.patch("scheduler.save_report", return_value=True) as save:
                    with mock.patch("scheduler.notify_scan_complete") as notify:
                        sched._run_scan(interval)
                        save.assert_called_once()
                        notify.assert_called_once_with(1, 1, 0)
                        sched.history.record.assert_called_once()
                        kwargs = sched.history.record.call_args.kwargs
                        self.assertEqual(kwargs["clean"], 1)
                        self.assertEqual(kwargs["infected"], 1)

    def test_run_scan_quarantines_when_auto_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            scan_target = tmp_path / "scan_me"
            scan_target.mkdir()
            evil = scan_target / "evil"
            evil.write_text("malware")

            sched = self._make_sched_with_mocks(tmp_path)
            results = [
                ScanResult(file_path=str(evil), status="infected", reason="X", sha256="a"),
            ]
            interval = {
                "name": "auto-q",
                "paths": [str(scan_target)],
                "auto_quarantine": True,
                "report_dir": str(tmp_path / "reports"),
            }

            with mock.patch("scheduler.scan_directory", return_value=results):
                with mock.patch("scheduler.save_report", return_value=True):
                    with mock.patch("scheduler.notify_scan_complete"):
                        with mock.patch("scheduler.quarantine_file") as quarantine:
                            sched._run_scan(interval)
                            quarantine.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
