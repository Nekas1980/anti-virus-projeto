# Quick Start

Get scanning in 5 minutes.

## Fastest Way

### 1. Scan a Directory (CLI)

```bash
python Virus_project.py /path/to/folder
```

Example:
```bash
python Virus_project.py ~/Downloads
```

**Output**: List of clean/infected files with hashes.

### 2. View Scan Report

Reports are saved to:
- `output/scan_report.json` — Machine-readable
- `output/scan_report.html` — Browser-friendly

Open HTML in your browser to see visual report.

---

## Using the GUI

```bash
python gui3.py
```

**Steps**:
1. Click "Adicionar Ficheiros" or drag & drop folders
2. Click "Scan"
3. View results in table
4. Click "Exportar Relatório" to save HTML

---

## Configuration

### Exclude Directories

Edit `exclusions.json`:

```json
{
  "exclusion_patterns": [
    "node_modules",
    ".git",
    "*.tmp"
  ]
}
```

Files matching patterns will be skipped.

### Add Known Malware Hashes

Edit `signatures.json`:

```json
{
  "malware_hashes": {
    "abc123def456...": "Trojan.Generic",
    "xyz789...": "Win32.Virus"
  }
}
```

Add SHA256 hashes of malware you want to detect.

---

## Scheduled Scanning

### Setup Schedule

```bash
# Generate example config
python scheduler.py create-config

# Edit schedule_config.json to your needs
nano schedule_config.json
```

### Run Scheduler

```bash
# Runs continuously, scans at scheduled times
python scheduler.py run
```

Reports saved to `scheduled_reports/scan_YYYYMMDD_HHMMSS.json`.

---

## Update Signatures from VirusTotal

### Get API Key

1. Go to https://www.virustotal.com
2. Sign up (free)
3. Get your API key from settings

### Run Update

```bash
export VIRUSTOTAL_API_KEY="your_key_here"
python virustotal_updater.py
```

Enter file hashes to check against VirusTotal database.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'colorama'"

```bash
pip install -r requirements.txt
```

### GUI doesn't open

```bash
# Verify tkinter is available
python -c "import tkinter; print('OK')"

# macOS: might need
brew install python-tk@3.11
```

### Tests fail

```bash
# Make sure you're in project directory
cd anti-virus-projeto

# Run from project root
python -m unittest test_virus_project -v
```

---

## Next Steps

- [How It Works](how-it-works.md) — Understand the scanning engine
- [Architecture](../architecture/architecture.md) — Deep dive into design
- [Contributing](../contribute/guidelines.md) — Help improve the project
