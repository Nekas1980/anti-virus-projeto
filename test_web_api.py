"""
Testes para ``web_api`` (Fase 3 / 3.3).

Skipped graciosamente quando FastAPI/httpx não estão instalados — a API é
opcional e não deve quebrar a suite quando ausente.
"""
from __future__ import annotations

import time
import unittest
from pathlib import Path

import web_api


def _has_test_client() -> bool:
    if not web_api._FASTAPI_AVAILABLE:
        return False
    try:
        from fastapi.testclient import TestClient  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipUnless(_has_test_client(), "FastAPI/httpx não instalados — API é opcional")
class TestWebAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fastapi.testclient import TestClient

        cls.app = web_api.create_app()
        cls.client = TestClient(cls.app)

    def setUp(self):
        web_api._reset_state_for_tests()

    def test_health(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")

    def test_scan_unknown_id_404(self):
        r = self.client.get("/api/scan/nope")
        self.assertEqual(r.status_code, 404)

    def test_scan_lifecycle(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.txt").write_bytes(b"clean a")
            (Path(tmp) / "b.txt").write_bytes(b"clean b")

            r = self.client.post("/api/scan", json={"paths": [tmp]})
            self.assertEqual(r.status_code, 200)
            scan_id = r.json()["scan_id"]

            for _ in range(40):
                state = self.client.get(f"/api/scan/{scan_id}").json()
                if state["status"] == "finished":
                    break
                time.sleep(0.1)
            else:
                self.fail("Scan não terminou em 4s")

            self.assertEqual(state["clean"], 2)
            self.assertEqual(state["infected"], 0)

            results = self.client.get(f"/api/scan/{scan_id}/results").json()
            self.assertEqual(len(results["results"]), 2)

    def test_history_endpoint(self):
        r = self.client.get("/api/history")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("scans", body)
        self.assertIn("count", body)

    def test_report_invalid_format_400(self):
        r = self.client.post("/api/scan", json={"paths": ["/nonexistent_path_xyz"]})
        scan_id = r.json()["scan_id"]
        for _ in range(30):
            if self.client.get(f"/api/scan/{scan_id}").json()["status"] == "finished":
                break
            time.sleep(0.05)

        r = self.client.get(f"/api/reports/{scan_id}/pdf")
        self.assertEqual(r.status_code, 400)


class TestModuleWithoutFastAPI(unittest.TestCase):
    """Testa que o módulo importa e degrada bem se FastAPI ausente."""

    def test_module_loads(self):
        self.assertTrue(hasattr(web_api, "_FASTAPI_AVAILABLE"))
        self.assertTrue(hasattr(web_api, "create_app"))

    def test_create_app_raises_when_unavailable(self):
        if web_api._FASTAPI_AVAILABLE:
            self.skipTest("FastAPI instalado — não há cenário de fallback a testar")
        with self.assertRaises(RuntimeError):
            web_api.create_app()


if __name__ == "__main__":
    unittest.main(verbosity=2)
