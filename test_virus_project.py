"""
Unit Tests para Virus_project.py

Testa funcionalidades principais do motor de varredura.
"""

import unittest
import json
import tempfile
from pathlib import Path
from Virus_project import (
    sha256_file,
    load_signatures,
    load_exclusions,
    scan_file,
    scan_directory,
    should_skip_path,
    add_signature,
    ScanResult,
)
from hash_cache import HashCache


class TestSHA256File(unittest.TestCase):
    """Testa cálculo de hash SHA256."""

    def test_sha256_valid_file(self):
        """Testa hash de um ficheiro válido."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = Path(tmp.name)

        try:
            hash_result = sha256_file(tmp_path)
            self.assertIsNotNone(hash_result)
            self.assertEqual(len(hash_result), 64)
            self.assertTrue(all(c in "0123456789abcdef" for c in hash_result))
        finally:
            tmp_path.unlink()

    def test_sha256_nonexistent_file(self):
        """Testa hash de ficheiro inexistente."""
        result = sha256_file(Path("/nonexistent/file.txt"))
        self.assertIsNone(result)

    def test_sha256_consistency(self):
        """Testa consistência do hash."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test")
            tmp_path = Path(tmp.name)

        try:
            hash1 = sha256_file(tmp_path)
            hash2 = sha256_file(tmp_path)
            self.assertEqual(hash1, hash2)
        finally:
            tmp_path.unlink()


class TestLoadSignatures(unittest.TestCase):
    """Testa carregamento de assinaturas."""

    def test_load_valid_signatures(self):
        """Testa carregamento de assinaturas válidas."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            data = {"malware_hashes": {"hash1": "Trojan", "hash2": "Virus"}}
            json.dump(data, tmp)
            tmp_path = Path(tmp.name)

        try:
            signatures = load_signatures(tmp_path)
            self.assertEqual(len(signatures), 2)
            self.assertEqual(signatures["hash1"], "Trojan")
        finally:
            tmp_path.unlink()

    def test_load_nonexistent_file(self):
        """Testa carregamento de arquivo inexistente."""
        signatures = load_signatures(Path("/nonexistent/signatures.json"))
        self.assertEqual(signatures, {})

    def test_load_invalid_json(self):
        """Testa carregamento de JSON inválido."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write("invalid json {")
            tmp_path = Path(tmp.name)

        try:
            signatures = load_signatures(tmp_path)
            self.assertEqual(signatures, {})
        finally:
            tmp_path.unlink()


class TestLoadExclusions(unittest.TestCase):
    """Testa carregamento de exclusões."""

    def test_load_valid_exclusions(self):
        """Testa carregamento de exclusões válidas."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            data = {"exclusion_patterns": ["node_modules", ".git", "*.tmp"]}
            json.dump(data, tmp)
            tmp_path = Path(tmp.name)

        try:
            exclusions = load_exclusions(tmp_path)
            self.assertEqual(len(exclusions), 3)
            self.assertIn("node_modules", exclusions)
        finally:
            tmp_path.unlink()

    def test_load_nonexistent_uses_default(self):
        """Testa que usa padrões padrão se arquivo não existe."""
        exclusions = load_exclusions(Path("/nonexistent/exclusions.json"))
        self.assertGreater(len(exclusions), 0)
        self.assertIn("node_modules", exclusions)


class TestShouldSkipPath(unittest.TestCase):
    """Testa função de exclusão."""

    def test_skip_directory_pattern(self):
        """Testa se ignora diretório com padrão."""
        patterns = ["node_modules", ".git"]
        path = Path("/project/node_modules/package")
        self.assertTrue(should_skip_path(path, patterns))

    def test_dont_skip_normal_path(self):
        """Testa se não ignora caminho normal."""
        patterns = ["node_modules", ".git"]
        path = Path("/project/src/main.py")
        self.assertFalse(should_skip_path(path, patterns))

    def test_skip_hidden_file(self):
        """Testa se ignora arquivo oculto."""
        patterns = [".env", ".DS_Store"]
        path = Path("/project/.env")
        self.assertTrue(should_skip_path(path, patterns))


class TestScanFile(unittest.TestCase):
    """Testa varredura de arquivo individual."""

    def test_scan_clean_file(self):
        """Testa varredura de arquivo limpo."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"clean file")
            tmp_path = Path(tmp.name)

        try:
            signatures = {}
            result = scan_file(tmp_path, signatures)
            self.assertEqual(result.status, "clean")
            self.assertIsNotNone(result.sha256)
        finally:
            tmp_path.unlink()

    def test_scan_infected_file(self):
        """Testa varredura de arquivo infectado."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"malware content")
            tmp_path = Path(tmp.name)

        try:
            file_hash = sha256_file(tmp_path)
            signatures = {file_hash: "TestTrojan"}
            result = scan_file(tmp_path, signatures)
            self.assertEqual(result.status, "infected")
            self.assertEqual(result.reason, "TestTrojan")
        finally:
            tmp_path.unlink()

    def test_scan_nonexistent_file(self):
        """Testa varredura de arquivo inexistente."""
        result = scan_file(Path("/nonexistent/file"), {})
        self.assertEqual(result.status, "skip")


class TestScanDirectory(unittest.TestCase):
    """Testa varredura recursiva de diretórios."""

    def test_scan_directory_basic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "file1.txt").write_bytes(b"content1")
            (root / "file2.txt").write_bytes(b"content2")
            (root / "subdir").mkdir()
            (root / "subdir" / "file3.txt").write_bytes(b"content3")

            results = scan_directory(root, {}, [])
            self.assertEqual(len(results), 3)
            paths = [Path(r.file_path).name for r in results]
            self.assertIn("file1.txt", paths)
            self.assertIn("file2.txt", paths)
            self.assertIn("file3.txt", paths)

    def test_scan_directory_with_exclusions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "clean.txt").write_bytes(b"clean")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "secret.exe").write_bytes(b"malware")
            (root / "venv").mkdir()
            (root / "venv" / "bin").mkdir()
            (root / "venv" / "bin" / "python").write_bytes(b"python")
            
            # Padrões que devem podar diretórios inteiros
            exclusions = ["node_modules", "venv"]
            
            results = scan_directory(root, {}, exclusions)
            
            # Deve encontrar apenas clean.txt
            self.assertEqual(len(results), 1)
            self.assertEqual(Path(results[0].file_path).name, "clean.txt")

    def test_scan_directory_with_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            scan_root = tmp_dir / "scan_target"
            scan_root.mkdir()
            
            file_path = scan_root / "test.txt"
            file_path.write_bytes(b"content")
            
            # Cache fora do scan_root para não ser contado como ficheiro
            cache_path = tmp_dir / "cache.db"
            cache = HashCache(cache_path)
            try:
                # Primeiro scan - popula cache
                results1 = scan_directory(scan_root, {}, [], cache=cache)
                self.assertEqual(len(results1), 1)
                
                # Modifica arquivo
                file_path.write_bytes(b"new content")
                results2 = scan_directory(scan_root, {}, [], cache=cache)
                self.assertEqual(len(results2), 1)
                self.assertNotEqual(results1[0].sha256, results2[0].sha256)
            finally:
                cache.close()


class TestAddSignature(unittest.TestCase):
    """Testa adição de assinaturas."""

    def test_add_new_signature(self):
        """Testa adição de nova assinatura."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump({"malware_hashes": {}}, tmp)
            tmp_path = Path(tmp.name)

        try:
            result = add_signature("abc123def456", "NewTrojan", tmp_path)
            self.assertTrue(result)

            signatures = load_signatures(tmp_path)
            self.assertEqual(signatures["abc123def456"], "NewTrojan")
        finally:
            tmp_path.unlink()

    def test_add_duplicate_signature(self):
        """Testa que não adiciona assinatura duplicada."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump({"malware_hashes": {"hash1": "Trojan"}}, tmp)
            tmp_path = Path(tmp.name)

        try:
            result = add_signature("hash1", "Virus", tmp_path)
            self.assertFalse(result)
        finally:
            tmp_path.unlink()


class TestScanResult(unittest.TestCase):
    """Testa dataclass ScanResult."""

    def test_scan_result_creation(self):
        """Testa criação de ScanResult."""
        result = ScanResult(file_path="/test/file", status="clean", sha256="abc123")
        self.assertEqual(result.file_path, "/test/file")
        self.assertEqual(result.status, "clean")
        self.assertEqual(result.sha256, "abc123")

    def test_scan_result_defaults(self):
        """Testa valores padrão de ScanResult."""
        result = ScanResult(file_path="/test", status="skip")
        self.assertEqual(result.reason, "")
        self.assertEqual(result.sha256, "")


class TestScanFileWithCache(unittest.TestCase):
    """Testa integração de scan_file com HashCache."""

    def test_cache_avoids_recomputation(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "file.bin"
            target.write_bytes(b"sample content")
            cache = HashCache(Path(tmp) / "cache.db")
            try:
                first = scan_file(target, {}, cache=cache)
                self.assertEqual(first.status, "clean")
                cached = cache.get(target)
                self.assertEqual(cached, first.sha256)

                cache.set(target, "deadbeef")
                second = scan_file(target, {"deadbeef": "FakeMalware"}, cache=cache)
                self.assertEqual(second.status, "infected")
                self.assertEqual(second.reason, "FakeMalware")
            finally:
                cache.close()


class TestSha256FileTimeout(unittest.TestCase):
    """Testa comportamento de timeout em sha256_file."""

    def test_zero_timeout_returns_none(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"x" * (2 * 1024 * 1024))
            tmp_path = Path(tmp.name)
        try:
            result = sha256_file(tmp_path, timeout=0.0)
            self.assertIsNone(result)
        finally:
            tmp_path.unlink()

    def test_no_timeout_completes_normally(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"small content")
            tmp_path = Path(tmp.name)
        try:
            result = sha256_file(tmp_path, timeout=None)
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 64)
        finally:
            tmp_path.unlink()


def run_tests():
    """Executa todos os testes."""
    unittest.main(argv=[""], exit=False, verbosity=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
