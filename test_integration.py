"""
Integration tests end-to-end (Fase 4 / 4.3).

Constroem um sandbox temporário, executam o pipeline completo (scan → cache →
relatórios HTML/JSON/Excel → quarentena) e validam o estado final do sistema
de ficheiros. Sem mocks dos componentes core — só fixtures reais.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import time
import unittest
from pathlib import Path

from excel_exporter import ExcelReportGenerator
from hash_cache import HashCache
from report_generator import HTMLReportGenerator, ReportMetadata, generate_json_report
from scan_history import ScanHistory
from Virus_project import (
    quarantine_file,
    save_report,
    scan_directory,
    sha256_file,
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class IntegrationSandbox:
    """Constrói uma estrutura realista para testar pipeline ponta-a-ponta."""

    def __init__(self, root: Path):
        self.root = root
        self.scan_dir = root / "scan_target"
        self.quarantine_dir = root / "quarantine"
        self.output_dir = root / "output"
        self.cache_db = root / "cache.db"
        self.history_db = root / "history.db"

        self.scan_dir.mkdir()
        self.quarantine_dir.mkdir()
        self.output_dir.mkdir()

        self.clean_payload = b"clean file content"
        self.evil_payload = b"this is a fake malware payload"
        self.clean_hash = _sha256_bytes(self.clean_payload)
        self.evil_hash = _sha256_bytes(self.evil_payload)

        # Ficheiros normais
        (self.scan_dir / "doc.txt").write_bytes(self.clean_payload)
        (self.scan_dir / "image.bin").write_bytes(b"another clean file")

        # Ficheiro malicioso (matching signature)
        (self.scan_dir / "evil.exe").write_bytes(self.evil_payload)

        # Subdirectoria a ser ignorada
        (self.scan_dir / "node_modules").mkdir()
        (self.scan_dir / "node_modules" / "ignored.js").write_bytes(b"should be skipped")

        # Subdirectoria normal com mais um clean
        sub = self.scan_dir / "subdir"
        sub.mkdir()
        (sub / "another.log").write_bytes(b"log content")

        self.signatures = {self.evil_hash: "TestMalware.IntegrationFake"}
        self.exclusions = ["node_modules", ".git", "__pycache__"]


class TestEndToEndScan(unittest.TestCase):
    def test_full_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = IntegrationSandbox(Path(tmp))

            cache = HashCache(sandbox.cache_db)
            history = ScanHistory(sandbox.history_db)
            try:
                started = time.time()
                results = scan_directory(
                    sandbox.scan_dir,
                    sandbox.signatures,
                    sandbox.exclusions,
                    cache=cache,
                )

                # node_modules deve ter sido ignorado
                file_paths = [r.file_path for r in results]
                self.assertFalse(any("node_modules" in p for p in file_paths))

                # 1 infected, 3 clean (doc.txt + image.bin + subdir/another.log)
                infected = [r for r in results if r.status == "infected"]
                clean = [r for r in results if r.status == "clean"]
                self.assertEqual(len(infected), 1)
                self.assertEqual(len(clean), 3)
                self.assertIn("evil.exe", infected[0].file_path)
                self.assertEqual(infected[0].reason, "TestMalware.IntegrationFake")

                # Cache populado: re-scan deve devolver os mesmos hashes
                cached_hash = cache.get(sandbox.scan_dir / "evil.exe")
                self.assertEqual(cached_hash, sandbox.evil_hash)

                # Reports
                metadata = ReportMetadata(
                    started_at=started,
                    finished_at=time.time(),
                    paths=[str(sandbox.scan_dir)],
                )
                json_path = sandbox.output_dir / "report.json"
                html_path = sandbox.output_dir / "report.html"
                xlsx_path = sandbox.output_dir / "report.xlsx"

                self.assertTrue(save_report(results, json_path))
                self.assertTrue(
                    HTMLReportGenerator.generate(results, html_path, metadata=metadata)
                )
                self.assertTrue(
                    generate_json_report(results, json_path, metadata=metadata)
                )

                if ExcelReportGenerator.is_available():
                    self.assertTrue(
                        ExcelReportGenerator.generate(
                            results, xlsx_path, metadata=metadata
                        )
                    )
                    self.assertTrue(xlsx_path.exists())

                # JSON enriquecido
                payload = json.loads(json_path.read_text(encoding="utf-8"))
                self.assertIn("metadata", payload)
                self.assertEqual(payload["counts"]["infected"], 1)
                self.assertEqual(payload["counts"]["clean"], 3)

                # HTML contém o nome da ameaça e o sumário executivo
                html = html_path.read_text(encoding="utf-8")
                self.assertIn("TestMalware.IntegrationFake", html)
                self.assertIn("Resumo Executivo", html)

                # History record
                history.record(
                    paths=[sandbox.scan_dir],
                    total=len(results),
                    clean=len(clean),
                    infected=len(infected),
                    skipped=0,
                    started_at=started,
                    report_path=html_path,
                )
                recent = history.recent(limit=5)
                self.assertEqual(len(recent), 1)
                self.assertEqual(recent[0].infected, 1)
                self.assertEqual(recent[0].clean, 3)

                # Quarantine: move infected → quarantine_dir
                evil = Path(infected[0].file_path)
                target = quarantine_file(evil, sandbox.quarantine_dir)
                self.assertIsNotNone(target)
                self.assertTrue(target.exists())
                self.assertFalse(evil.exists(), "ficheiro original deve ter sido movido")

                # Re-quarantine de outro ficheiro com mesmo nome → suffix anti-colisão
                duplicate = sandbox.scan_dir / "evil.exe"
                duplicate.write_bytes(b"another evil with same name")
                target2 = quarantine_file(duplicate, sandbox.quarantine_dir)
                self.assertIsNotNone(target2)
                self.assertNotEqual(target2.name, target.name)
            finally:
                cache.close()
                history.close()

    def test_rescan_uses_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = IntegrationSandbox(Path(tmp))
            cache = HashCache(sandbox.cache_db)
            try:
                # First scan populates cache
                scan_directory(
                    sandbox.scan_dir, sandbox.signatures, sandbox.exclusions, cache=cache
                )
                self.assertEqual(
                    cache.get(sandbox.scan_dir / "doc.txt"), sandbox.clean_hash
                )

                # Second scan: cache hit — verificamos que sha256_file não é
                # chamado para ficheiros já em cache (mocking via spy)
                from unittest import mock as _m

                with _m.patch(
                    "Virus_project.sha256_file", side_effect=sha256_file
                ) as spy:
                    scan_directory(
                        sandbox.scan_dir,
                        sandbox.signatures,
                        sandbox.exclusions,
                        cache=cache,
                    )
                    # Nenhum ficheiro mudou → spy não deve ser chamado
                    # (cache.get devolve hash sem recomputar)
                    self.assertEqual(spy.call_count, 0)
            finally:
                cache.close()

    def test_modified_file_invalidates_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = IntegrationSandbox(Path(tmp))
            cache = HashCache(sandbox.cache_db)
            try:
                scan_directory(
                    sandbox.scan_dir, sandbox.signatures, sandbox.exclusions, cache=cache
                )

                # Modifica conteúdo (mtime e size alteram)
                target = sandbox.scan_dir / "doc.txt"
                time.sleep(0.05)
                target.write_bytes(b"completely different content now, much longer")

                # Cache deve ter invalidado para este ficheiro
                self.assertIsNone(cache.get(target))

                results = scan_directory(
                    sandbox.scan_dir, sandbox.signatures, sandbox.exclusions, cache=cache
                )
                doc_result = next(r for r in results if r.file_path.endswith("doc.txt"))
                self.assertEqual(doc_result.status, "clean")
                # Novo hash deve ser diferente do clean_hash original
                self.assertNotEqual(doc_result.sha256, sandbox.clean_hash)
            finally:
                cache.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
