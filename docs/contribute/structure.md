# Project Structure

Overview of files and directories.

## Directory Tree

```
anti-virus-projeto/
│
├── 📄 Virus_project.py              # Core scanning engine
├── 📄 gui.py                        # Simple Tkinter GUI
├── 📄 gui2.py                       # GUI v2 with threading
├── 📄 gui3.py                       # GUI v3 (recommended)
├── 📄 report_generator.py           # HTML/JSON report generation
├── 📄 scheduler.py                  # Background task scheduling
├── 📄 virustotal_updater.py         # Threat intelligence API
│
├── 🧪 test_virus_project.py         # Unit tests (18 tests)
│
├── ⚙️ setup.py                       # PyPI packaging
├── ⚙️ pyproject.toml               # Modern Python config
├── ⚙️ build_exe.spec               # PyInstaller config
│
├── 📋 requirements.txt              # Dependencies
├── 📋 signatures.json               # Malware hash database
├── 📋 exclusions.json               # Directory exclusion patterns
├── 📋 schedule_config.json          # Scheduler config (generated)
│
├── 📚 README.md                     # User documentation
├── 📚 DEVELOPMENT.md                # Development guide
├── 📚 ARCHITECTURE.md               # Technical design
├── 📚 CONTRIBUTING.md               # Contribution guidelines
├── 📚 BUILD_INSTRUCTIONS.md         # Distribution guide
├── 📚 SESSION_SUMMARY.md            # Session improvements
│
├── 📁 docs/                         # MkDocs documentation
│   ├── index.md                     # Homepage
│   ├── mkdocs.yml                   # MkDocs configuration
│   ├── guides/
│   │   ├── installation.md
│   │   ├── quickstart.md
│   │   └── how-it-works.md
│   ├── architecture/
│   │   ├── architecture.md
│   │   ├── development.md
│   │   └── build.md
│   ├── contribute/
│   │   ├── guidelines.md
│   │   ├── structure.md (this file)
│   │   └── roadmap.md
│   └── about/
│       ├── license.md
│       └── session-summary.md
│
├── .github/
│   └── workflows/
│       ├── tests.yml                # GitHub Actions CI/CD
│       └── deploy.yml               # MkDocs deploy (new)
│
├── 📁 output/                       # Generated reports (created on run)
│   ├── scan_report.html
│   └── scan_report.json
│
├── 📁 quarantine/                   # Infected files (created on run)
│   └── (moved infected files)
│
├── 📁 scheduled_reports/            # Timestamped reports (scheduler)
│   └── scan_YYYYMMDD_HHMMSS.json
│
├── 📁 .git/                         # Git repository
│
├── .gitignore                       # Git ignore rules
├── LICENSE                          # MIT License
└── .env (not in repo)              # API keys (VIRUSTOTAL_API_KEY)
```

## Core Modules

### `Virus_project.py` (500 lines)
**Scanning engine** — Main entry point

Key classes:
- `ScanResult` — Dataclass with file scan result

Key functions:
- `sha256_file(path)` — Compute file hash
- `load_signatures(path)` — Load malware database
- `load_exclusions(path)` — Load skip patterns
- `should_skip_path(path, patterns)` — Check if path matches exclusion
- `scan_file(path, signatures)` — Scan single file
- `scan_directory(path, sigs, excl)` — Recursively scan directory
- `quarantine_file(path, dest)` — Move infected file
- `add_signature(hash, name, path)` — Add new malware entry

### `report_generator.py` (150 lines)
**Report generation** — HTML & JSON export

Classes:
- `HTMLReportGenerator` — Generates styled HTML reports

Functions:
- `generate_json_report(results, output_file)` — JSON export

### `scheduler.py` (200 lines)
**Task automation** — Background scanning

Classes:
- `ScanScheduler` — Manages scheduled scans

Key methods:
- `_load_config()` — Load schedule configuration
- `_should_run_now(interval)` — Check if time matches schedule
- `_run_scan(interval)` — Execute scan
- `run()` — Main loop
- `create_schedule_config()` — Generate example config

### `virustotal_updater.py` (150 lines)
**API integration** — External threat intelligence

Functions:
- `get_virustotal_key()` — Read API key from environment
- `fetch_vt_hash_info(hash, key)` — Query VirusTotal
- `is_malware(vt_data)` — Check if malicious
- `extract_malware_name(vt_data)` — Get threat name
- `batch_update(hashes, path)` — Update multiple hashes
- `update_single_hash(hash, path)` — Update single hash

### `gui.py`, `gui2.py`, `gui3.py` (300+ lines)
**User interfaces** — Tkinter-based GUIs

Features:
- File/folder selection
- Progress display
- Results table
- Report export

## Configuration Files

### `signatures.json`
Malware hash database:
```json
{
  "malware_hashes": {
    "hash1": "Threat.Name1",
    "hash2": "Threat.Name2"
  }
}
```

### `exclusions.json`
Directory patterns to skip:
```json
{
  "exclusion_patterns": [
    "node_modules",
    ".git",
    "*.tmp"
  ]
}
```

### `schedule_config.json`
Scheduler configuration (auto-generated):
```json
{
  "enabled": true,
  "auto_quarantine": false,
  "keep_logs": 30,
  "intervals": [...]
}
```

### `mkdocs.yml`
Documentation configuration:
- Navigation structure
- Theme (Material for MkDocs)
- Plugins (search, mkdocstrings)

## Test Files

### `test_virus_project.py` (400+ lines)
18 comprehensive unit tests:

Test classes:
- `TestSHA256File` — Hash computation (3 tests)
- `TestLoadSignatures` — Signature loading (3 tests)
- `TestLoadExclusions` — Exclusion loading (2 tests)
- `TestShouldSkipPath` — Path filtering (3 tests)
- `TestScanFile` — Single file scanning (3 tests)
- `TestAddSignature` — Adding malware entries (2 tests)
- `TestScanResult` — Data structure (1 test)

## CI/CD Files

### `.github/workflows/tests.yml`
Automated testing pipeline:
- 3 OS: Ubuntu, macOS, Windows
- 4 Python versions: 3.9, 3.10, 3.11, 3.12
- Total: 12 test matrices per commit

### `.github/workflows/deploy.yml` (new)
MkDocs deployment:
- Build documentation on each push
- Deploy to GitHub Pages automatically

## Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | User-facing overview |
| `ARCHITECTURE.md` | Technical design & modules |
| `DEVELOPMENT.md` | Dev setup & workflow |
| `CONTRIBUTING.md` | Contribution guidelines |
| `BUILD_INSTRUCTIONS.md` | Distribution & packaging |
| `SESSION_SUMMARY.md` | Session improvements & roadmap |
| `docs/` | Full MkDocs documentation |

## Typical Workflow

1. **User runs scan**:
   - `python Virus_project.py ~/Downloads`
   - Loads `signatures.json` + `exclusions.json`
   - Generates report in `output/`

2. **Developer contributes**:
   - Edits source files
   - Runs: `python -m unittest test_virus_project -v`
   - Commits to GitHub
   - GitHub Actions runs 18 tests on 12 environments

3. **Admin schedules scan**:
   - Edits `schedule_config.json`
   - Runs: `python scheduler.py run`
   - Generates timestamped reports in `scheduled_reports/`

## Adding a New File

If you add a new module:
1. Add to project root (if core) or subdirectory
2. Add unit tests to `test_virus_project.py`
3. Update `.gitignore` if needed
4. Document in `ARCHITECTURE.md`
5. Update this file
6. Commit with clear message

## Customization Points

- **Signatures**: Edit `signatures.json` to add malware hashes
- **Exclusions**: Edit `exclusions.json` to skip directories
- **Schedule**: Generate and edit `schedule_config.json`
- **GUI**: Modify `gui3.py` for interface changes
- **Reports**: Customize `report_generator.py` templates
- **API**: Add new endpoints in integration modules

## Size & Stats

| Metric | Value |
|--------|-------|
| **Core Python** | ~500 lines |
| **GUIs** | ~300 lines |
| **Tests** | ~400 lines |
| **Documentation** | ~2000 lines |
| **Config files** | 3 JSON files |
| **External modules** | 2 (colorama, requests) |

## Next Steps

- [Contributing Guidelines](guidelines.md) — How to contribute
- [Roadmap](roadmap.md) — Future improvements
- [Development](../architecture/development.md) — Setup guide
