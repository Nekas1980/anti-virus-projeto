# 🏗️ Architecture & Design

This document describes the technical architecture of Antivírus Projeto, design decisions, and how components interact.

---

## 🎓 Educational Objective

This project teaches fundamental cybersecurity concepts through a **signature-based malware detection engine**:

- **File integrity**: How hashing (SHA256) uniquely identifies files
- **Pattern matching**: Comparing computed values against known databases
- **Configuration management**: Loading and applying exclusion rules
- **External APIs**: Integrating with third-party threat intelligence (VirusTotal)
- **Automation**: Scheduling tasks and generating reports
- **Software engineering**: Testing, logging, and production distribution

---

## 🏛️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface Layer                    │
├─────────────────────────────────────────────────────────────┤
│  gui.py (Tkinter)  │  CLI (Virus_project.py)  │  Web (TBD) │
└──────────┬──────────────────────┬──────────────────────────┘
           │                      │
           └──────────┬───────────┘
                      │
┌─────────────────────┴────────────────────────────────────────┐
│              Scanning Engine Layer                            │
├──────────────────────────────────────────────────────────────┤
│ Virus_project.py:                                            │
│  • scan_file(file, signatures) → ScanResult                 │
│  • scan_directory(path, signatures, exclusions)             │
│  • sha256_file(path) → hash                                 │
│  • load_signatures(json_file) → Dict[hash, name]            │
│  • load_exclusions(json_file) → List[patterns]              │
│  • should_skip_path(path, patterns) → bool                  │
└──────────┬──────────────────────────────────────────────────┘
           │
┌──────────┴──────────────────────────────────────────────────┐
│            Support & Integration Layer                       │
├──────────────────────────────────────────────────────────────┤
│ • virustotal_updater.py   (API integration)                 │
│ • scheduler.py            (Task scheduling)                 │
│ • report_generator.py     (Output generation)               │
│ • logging module          (Audit trail)                     │
└──────────┬──────────────────────────────────────────────────┘
           │
┌──────────┴──────────────────────────────────────────────────┐
│              Data & Configuration Layer                      │
├──────────────────────────────────────────────────────────────┤
│ JSON Files:                                                  │
│  • signatures.json   (known malware hashes)                 │
│  • exclusions.json   (directory patterns to skip)           │
│  • schedule_config.json (scheduled scan config)             │
│ Directories:                                                 │
│  • quarantine/      (isolated infected files)               │
│  • output/          (generated reports)                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 📦 Core Modules

### 1. `Virus_project.py` — Scanning Engine

**Purpose**: Main malware detection engine

**Key Data Structures**:

```python
@dataclass
class ScanResult:
    file_path: str          # Path to scanned file
    status: str             # 'clean', 'infected', 'skip'
    reason: str             # Malware name if infected
    sha256: str             # Computed file hash
```

**Key Functions**:

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `sha256_file(path)` | Path | str \| None | Compute file hash |
| `load_signatures(path)` | Path | Dict | Load malware database |
| `load_exclusions(path)` | Path | Dict | Load skip patterns |
| `should_skip_path(path, patterns)` | Path, List | bool | Check if path matches exclusion |
| `scan_file(path, signatures)` | Path, Dict | ScanResult | Scan single file |
| `scan_directory(path, sigs, excl)` | Path, Dict, Dict | List[ScanResult] | Recursively scan directory |
| `add_signature(hash, name, path)` | str, str, Path | bool | Add new malware entry |
| `quarantine_file(path, dest)` | Path, Path | bool | Move infected file |

**Algorithm**:

```
scan_directory(path, signatures, exclusions):
    results = []
    for each file/folder in path:
        if should_skip_path(file, exclusions):
            skip
        if is_directory:
            results += scan_directory(file, ...)  # Recursion
        else:
            hash = sha256_file(file)
            if hash in signatures:
                result = INFECTED
            else:
                result = CLEAN
            results.append(ScanResult(...))
    return results
```

**Design Decisions**:

- ✅ **Recursive scanning**: Processes subdirectories automatically
- ✅ **Configurable exclusions**: Patterns allow skipping large/irrelevant directories
- ✅ **Streaming hash computation**: Handles large files efficiently (1MB chunks)
- ✅ **Error resilience**: Continues scanning even if individual files fail
- ⚠️ **Signature-only detection**: No heuristics or behavior analysis (educational limitation)

---

### 2. `report_generator.py` — Report Generation

**Purpose**: Convert scan results into user-friendly reports

**Classes**:

- `HTMLReportGenerator`: Generates styled HTML reports
  - `HTML_TEMPLATE`: Complete HTML5 document with embedded CSS
  - `generate(results, output_file, include_summary)`: Main method

- `generate_json_report()`: Function for JSON export

**Features**:

- 📊 Statistics cards (total, clean, infected, skipped)
- ⚠️ Threat table (infected files with hashes)
- 📋 Summary table (all results with status)
- 🎨 Responsive CSS design (mobile-friendly)
- 🖨️ Print-friendly styling

**Design Decisions**:

- ✅ **Embedded CSS**: Reports are self-contained (no external assets)
- ✅ **Responsive grid**: Adapts to different screen sizes
- ✅ **Color-coded status**: Visual distinction between clean/infected/skipped
- ✅ **Hash truncation**: Shows first 32 chars of SHA256 for readability
- ⚠️ **Hardcoded limits**: Summary shows max 50 results

---

### 3. `virustotal_updater.py` — Threat Intelligence Integration

**Purpose**: Update signature database from VirusTotal API

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `get_virustotal_key()` | Read API key from environment |
| `fetch_vt_hash_info(hash, key)` | Query VirusTotal for single hash |
| `is_malware(vt_data)` | Check if vendors flagged as malicious |
| `extract_malware_name(vt_data)` | Get threat classification |
| `batch_update(hashes, path)` | Update multiple hashes with progress |
| `update_single_hash(hash, path)` | Update single hash in database |

**API Integration**:

```
VirusTotal API v3:
  Endpoint: https://www.virustotal.com/api/v3/files/{hash}
  Header: x-apikey: {VIRUSTOTAL_API_KEY}
  Response: {last_analysis_stats: {malicious: N, ...}, names: [...]}
```

**Design Decisions**:

- ✅ **Optional integration**: Works without API key (graceful degradation)
- ✅ **Environment variable**: Secure API key management
- ✅ **Error handling**: Continues on API failures (rate limits, offline)
- ✅ **Batch updates**: Efficient processing of multiple hashes
- ⚠️ **Rate limiting**: VirusTotal free API has quotas (~4 req/min)

---

### 4. `scheduler.py` — Automated Scanning

**Purpose**: Execute scans on a schedule (background task)

**Class**: `ScanScheduler`

**Key Methods**:

| Method | Purpose |
|--------|---------|
| `_load_config()` | Load schedule_config.json |
| `_should_run_now(interval)` | Check if current time matches schedule |
| `_run_scan(interval)` | Execute scan for given interval |
| `run()` | Main loop (runs continuously) |
| `create_schedule_config()` | Generate example configuration |

**Configuration Format** (schedule_config.json):

```json
{
  "enabled": true,
  "auto_quarantine": false,
  "keep_logs": 30,
  "intervals": [
    {
      "name": "daily_morning",
      "hour": 9,
      "minute": 0,
      "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
      "paths": ["/home/user/Downloads"],
      "auto_quarantine": false
    }
  ]
}
```

**Scheduling Logic**:

```
run():
    while running:
        for each interval in config:
            now = current_time
            schedule_time = today at interval.hour:minute
            time_diff = |now - schedule_time|
            if time_diff < 60 seconds AND day_matches:
                run_scan(interval)
        sleep(30 seconds)
```

**Design Decisions**:

- ✅ **Interval-based scheduling**: Simple, doesn't require cron/Task Scheduler knowledge
- ✅ **Graceful shutdown**: SIGINT handler for clean exit
- ✅ **Auto-quarantine option**: Can automatically isolate infected files
- ✅ **Report generation**: Each scan produces timestamped report
- ⚠️ **Simple timing**: ±60 second windows (not sub-minute precision)

---

### 5. `gui.py` — User Interface

**Purpose**: Tkinter-based graphical interface

**Key Components**:

| Component | Purpose |
|-----------|---------|
| `ScannerApp` class | Main application window |
| `fazer_scan_multiplas()` | Select files/folders and initiate scan |
| `exibir_resultados()` | Display results in table |
| `exportar_relatorio()` | Generate and save HTML report |

**Threading**:

- Main thread: GUI event loop
- Worker thread: Scanning (prevents UI freeze)
- Queue: Results passed from worker to main thread

**Design Decisions**:

- ✅ **Threading**: Non-blocking UI during long scans
- ✅ **Drag-and-drop**: Users can add files/folders
- ✅ **Progress feedback**: Results update in real-time
- ✅ **Export capability**: Save reports directly from GUI
- ⚠️ **Single-threaded Tkinter**: Complex concurrency avoided

---

## 🔄 Data Flow Examples

### Example 1: User Scans a Directory

```
gui.py:fazer_scan_multiplas()
  ↓ User selects /home/user/Downloads
  ↓
Virus_project.py:scan_directory()
  ├→ load_signatures(signatures.json)
  ├→ load_exclusions(exclusions.json)
  └→ for each file in directory:
      ├→ should_skip_path(file, exclusions)?
      │   └→ match against fnmatch patterns
      ├→ sha256_file(file)
      │   └→ compute SHA256 hash
      ├→ hash in signatures?
      │   └→ ScanResult(status='infected'|'clean')
      └→ yield result to GUI
  ↓
gui.py:exibir_resultados()
  └→ Display results in table
  └→ User can export to HTML
      ↓
report_generator.py:HTMLReportGenerator.generate()
  └→ Format results as styled HTML
  └→ Save to output/scan_report.html
```

### Example 2: Administrator Updates Signatures via VirusTotal

```
User runs: export VIRUSTOTAL_API_KEY="..." && python virustotal_updater.py
  ↓
virustotal_updater.py:main()
  ├→ get_virustotal_key() → read env var
  ├→ prompt for hashes to update
  └→ for each hash:
      ├→ fetch_vt_hash_info(hash, key)
      │   └→ API call to VirusTotal
      ├→ is_malware(response)?
      ├→ extract_malware_name(response)
      └→ add_signature(hash, name, signatures.json)
  ↓
signatures.json updated with new malware entries
```

### Example 3: Scheduled Scan at Night

```
User runs: python scheduler.py create-config  → generates schedule_config.json
User edits: schedule_config.json (set hour=22)
User runs: python scheduler.py run
  ↓
scheduler.py:ScanScheduler.run()
  └→ Loop every 30 seconds:
      ├→ Check if now ≈ 22:00
      ├→ If yes, call _run_scan()
      │   ├→ load_signatures()
      │   ├→ load_exclusions()
      │   └→ scan_directory(/home/user/Downloads, ...)
      ├→ Save report to scheduled_reports/scan_YYYYMMDD_HHMMSS.json
      ├→ If infected files found AND auto_quarantine=true:
      │   └→ quarantine_file() → move to quarantine/
      └→ Log results
```

---

## 🔐 Security Considerations

### What This Project DOES

✅ **Demonstrates hash-based verification** — users learn how file integrity checking works
✅ **Shows API integration patterns** — practical external service usage
✅ **Teaches logging and audit trails** — important for security systems
✅ **Illustrates pattern matching** — foundational to intrusion detection

### What This Project DOES NOT

❌ **Real-time monitoring** — no file system watchers
❌ **Heuristic analysis** — no behavior-based detection
❌ **Encryption/sandboxing** — no containment mechanisms
❌ **Machine learning models** — no statistical anomaly detection
❌ **Production-grade performance** — not optimized for scale

### Limitations

⚠️ **Signature-based only**: Attackers can evade by modifying files (hash collision is impractical, but one-byte change breaks matching)
⚠️ **No polymorphic detection**: Can't detect variants unless all variants are in database
⚠️ **Single-threaded scanning**: Processes files sequentially (slow on large directories)
⚠️ **No update mechanism**: Requires manual API calls to refresh signatures
⚠️ **Not real-time**: Only scans when explicitly requested or scheduled

---

## 📊 Data Persistence

### Files

**JSON Databases**:
- `signatures.json` — Malware hashes {hash → name}
- `exclusions.json` — Exclusion patterns
- `schedule_config.json` — Scheduler configuration

**Reports**:
- `output/scan_report.html` — Last HTML report
- `output/scan_report.json` — Last JSON report
- `scheduled_reports/scan_YYYYMMDD_HHMMSS.json` — Timestamped reports

**Logs**:
- `scan.log` — Scan operations and errors
- `schedule.log` — Scheduler activity

**Quarantine**:
- `quarantine/` — Directory containing isolated infected files

---

## 🧪 Testing Strategy

**Test Coverage**: 18 unit tests covering:

| Module | Tests | Coverage |
|--------|-------|----------|
| SHA256 hashing | 3 | File computation, nonexistent files, consistency |
| Signature loading | 3 | Valid JSON, missing files, invalid JSON |
| Exclusion loading | 2 | Valid patterns, default fallback |
| Path filtering | 3 | Directory patterns, normal paths, hidden files |
| File scanning | 3 | Clean files, infected files, nonexistent files |
| Signature addition | 2 | New signatures, duplicate prevention |
| Data structures | 1 | ScanResult creation and defaults |

**CI/CD**: GitHub Actions tests on:
- 3 OS (Ubuntu, macOS, Windows)
- 4 Python versions (3.9, 3.10, 3.11, 3.12)
- Result: 12 test matrices × 18 tests = 216 test runs per commit

---

## 🚀 Deployment Models

### 1. **Source Distribution** (Educational)
- Users clone repo and run with Python
- Requires Python 3.9+ installed
- Best for learning/modification

### 2. **PyPI Package** (Community)
```bash
pip install antivirus-projeto
antivirus-scan ~/Downloads
```
- Cross-platform via pip
- Includes CLI entry points

### 3. **Standalone Executable** (End-Users)
```bash
# Download antivirus_projeto.exe (Windows)
antivirus_projeto.exe C:\Downloads
```
- No Python required
- Single file, 50MB+ size

### 4. **Docker Container** (DevOps)
```bash
docker run antivirus-projeto:1.0.0 /home/user/Downloads
```
- Containerized environment
- Consistent across systems

---

## 🎓 Learning Pathways

**Beginner**: Understand hash verification and pattern matching
1. Read `Virus_project.py`
2. Run: `python Virus_project.py ~/Downloads`
3. Examine `signatures.json` format

**Intermediate**: Learn automation and reporting
1. Study `scheduler.py` timing logic
2. Explore `report_generator.py` HTML templating
3. Modify `schedule_config.json` for custom schedules

**Advanced**: Integrate external services and build extensions
1. Study `virustotal_updater.py` API patterns
2. Implement custom report formats
3. Add new data sources (YARA rules, OSINT feeds)

---

## 📝 Design Principles

1. **Clarity over cleverness**: Simple, understandable code
2. **Educational focus**: Each component teaches a concept
3. **Fail gracefully**: Errors logged, scanning continues
4. **Configuration-driven**: Behavior controlled by JSON files
5. **No external dependencies**: Minimal, well-known libraries only
6. **Cross-platform**: Works on Windows, macOS, Linux

---

**For detailed development setup, see [DEVELOPMENT.md](DEVELOPMENT.md)**
**For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)**
