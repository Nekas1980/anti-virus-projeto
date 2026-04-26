from __future__ import annotations
import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

BUFFER_SIZE = 1024 * 1024

@dataclass
class ScanResult:
    file_path: str
    status: str
    reason: str = ""
    sha256: str = ""

def sha256_file(file_path: Path) -> str:
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def load_signatures(signature_file: Path) -> Dict[str, str]:
    if not signature_file.exists():
        return {}
    with signature_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("malware_hashes", {})

def scan_file(file_path: Path, signatures: Dict[str, str]) -> ScanResult:
    if not file_path.is_file():
        return ScanResult(file_path=str(file_path), status="skip", reason="não é ficheiro")
    digest = sha256_file(file_path)
    threat_name = signatures.get(digest)
    if threat_name:
        return ScanResult(
            file_path=str(file_path),
            status="infected",
            reason=threat_name,
            sha256=digest,
        )
    return ScanResult(
        file_path=str(file_path),
        status="clean",
        sha256=digest,
    )

def scan_directory(root: Path, signatures: Dict[str, str]) -> List[ScanResult]:
    results: List[ScanResult] = []
    for path in root.rglob("*"):
        if path.is_file():
            results.append(scan_file(path, signatures))
    return results

def quarantine_file(file_path: Path, quarantine_dir: Path) -> Path:
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    target = quarantine_dir / file_path.name
    counter = 1
    while target.exists():
        target = quarantine_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
        counter += 1
    shutil.move(str(file_path), str(target))
    return target

def save_report(results: List[ScanResult], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "file_path": r.file_path,
            "status": r.status,
            "reason": r.reason,
            "sha256": r.sha256,
        }
        for r in results
    ]
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

def main() -> None:
    target_dir_input = input("Diretório para escanear: ").strip()
    target_dir = Path(target_dir_input)
    if not target_dir.exists() or not target_dir.is_dir():
        print("Diretório inválido.")
        return
    signatures = load_signatures(Path("signatures.json"))
    results = scan_directory(target_dir, signatures)
    infected = [r for r in results if r.status == "infected"]
    clean = [r for r in results if r.status == "clean"]
    print(f"Arquivos limpos: {len(clean)}")
    print(f"Arquivos suspeitos/infectados: {len(infected)}")
    for item in infected:
        print(f"[INFECTADO] {item.file_path} -> {item.reason}")
    save_report(results, Path("output/scan_report.json"))
    choice = input("Mover infectados para quarentena? (s/n): ").strip().lower()
    if choice == "s":
        quarantine_dir = Path("quarantine")
        for item in infected:
            quarantine_file(Path(item.file_path), quarantine_dir)
        print("Quarentena concluída.")

if __name__ == "__main__":
    main()