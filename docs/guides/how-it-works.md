# How It Works

Understanding signature-based malware detection.

## The Scanning Process

```
User selects folder to scan
         ↓
Load malware signatures (SHA256 hashes)
         ↓
For each file in folder (recursively):
  ├─ Check if should skip (exclusion patterns)
  ├─ Compute file's SHA256 hash
  ├─ Compare against signature database
  └─ Mark as CLEAN or INFECTED
         ↓
Generate report (HTML, JSON)
         ↓
(Optional) Quarantine infected files
```

## What is SHA256?

SHA256 is a cryptographic hash function that:
- Takes any file as input
- Produces a unique 64-character fingerprint
- Same file always produces same hash
- Different file produces different hash

**Example**:
```
File: clean.exe
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

File: malware.exe (1 byte different)
SHA256: d41d8cd98f00b204e9800998ecf8427eabcdef0000000000000000000000000000

→ Completely different!
```

## Signature Database

A signature is: `{hash: threat_name}`

```json
{
  "malware_hashes": {
    "abc123...": "Trojan.Generic",
    "def456...": "Win32.Virus"
  }
}
```

If computed hash matches any signature → file is **infected**.

## Exclusion Patterns

Skip directories to save time:

```json
{
  "exclusion_patterns": [
    "node_modules",      # npm packages
    ".git",              # git history
    "System32",          # Windows system
    "*/cache/*"          # Temporary caches
  ]
}
```

Uses glob-style patterns (fnmatch):
- `*.tmp` — matches any file ending in .tmp
- `*/temp/*` — matches temp in any subdirectory
- `node_modules` — exact directory name

## Example Scan Flow

```
Scan ~/Downloads

Check ~/Downloads/document.pdf
├─ Hash: e3b0c44...
├─ In signatures? No
└─ Result: ✅ CLEAN

Check ~/Downloads/game.exe
├─ Hash: abc123...
├─ In signatures? YES → "Trojan.Generic"
└─ Result: ⚠️ INFECTED

Check ~/Downloads/archive.zip
├─ Is it archive? Treated as single file
├─ Hash: xyz789...
├─ In signatures? No
└─ Result: ✅ CLEAN

(Repeat for each file)

Final Report:
- Total: 3 files
- Clean: 2
- Infected: 1
```

## Components

### 1. Scanner (`Virus_project.py`)
- Compute hashes
- Load signatures and exclusions
- Recursively scan directories
- Generate results

### 2. Report Generator (`report_generator.py`)
- Format results as HTML/JSON
- Create statistics
- Highlight threats

### 3. Scheduler (`scheduler.py`)
- Run scans automatically at scheduled times
- Runs in background
- Generates timestamped reports

### 4. API Integration (`virustotal_updater.py`)
- Query VirusTotal API
- Download new threat intelligence
- Update local signature database

## Limitations (Why It's Educational)

### What Signature Detection Does Well
✅ Detects known malware instantly  
✅ No false positives (hash matches are certain)  
✅ Works offline  
✅ Fast and lightweight  

### What It Cannot Detect
❌ New/unknown malware (not in database)  
❌ Polymorphic malware (modified hashes)  
❌ Behavior-based threats  
❌ Legitimate software used maliciously  

### Real Antivirus Software Uses
- **Heuristics** — Analyze suspicious behavior patterns
- **Machine Learning** — Statistical anomaly detection
- **Sandboxing** — Run suspicious files safely
- **Real-time monitoring** — Watch file system events
- **Cloud analysis** — Share detection across millions of users

## Why Learn Hash-Based Detection?

This simple approach teaches:
- **Cryptographic hashing** — Foundational security concept
- **Pattern matching** — Core algorithm in many tools
- **File system traversal** — Important for system tools
- **Configuration management** — How to parameterize behavior
- **External APIs** — Integration patterns
- **Testing & automation** — Professional software practices

## Next Steps

- [Quick Start](quickstart.md) — Run your first scan
- [Architecture](../architecture/architecture.md) — Design details
- [Development](../architecture/development.md) — Modify the code
