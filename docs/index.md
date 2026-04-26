# Antivírus Projeto

**Educational malware detection engine demonstrating cybersecurity fundamentals.**

An open-source Python project teaching hash-based malware scanning, pattern matching, file system traversal, API integration, and security best practices.

## 🎓 Educational Objective

Learn how antivirus software works by building a signature-based detection engine:

- **File integrity**: How SHA256 hashing uniquely identifies files
- **Pattern matching**: Comparing computed values against known malware databases
- **Configuration management**: Loading and applying exclusion rules
- **External APIs**: Integrating with VirusTotal threat intelligence
- **Automation**: Scheduling tasks and generating reports
- **Software engineering**: Testing, logging, and production distribution

## ⚠️ Important Disclaimer

**This project is for EDUCATIONAL PURPOSES ONLY.** It is NOT production-ready and should NOT be used as a primary antivirus solution. It demonstrates basic malware scanning concepts and is intended for learning, not real-world protection.

## ✨ Features

- 🔍 **Signature-based scanning** — Detects malware by SHA256 hash comparison
- 📁 **Recursive directory scanning** — Analyzes all subdirectories automatically
- ⚙️ **Configurable exclusions** — Skip directories with pattern matching
- 📊 **HTML & JSON reports** — Export scan results in multiple formats
- 🕐 **Scheduled scanning** — Automate scans with interval-based scheduling
- 🌐 **VirusTotal API** — Update signatures from external threat intelligence
- 🖥️ **Multiple interfaces** — CLI, GUI (Tkinter), and batch processing
- 🧪 **18 unit tests** — Comprehensive test coverage across Python 3.9-3.12
- 🤖 **CI/CD pipeline** — Automated testing on 12 environments (3 OS × 4 Python versions)

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or later
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/Nekas1980/anti-virus-projeto.git
cd anti-virus-projeto

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Scanner

```bash
# CLI mode
python Virus_project.py /path/to/scan

# GUI mode
python gui3.py

# Scheduler (background scans)
python scheduler.py create-config
python scheduler.py run
```

## 📚 Documentation

- **[Getting Started](guides/installation.md)** — Setup and first steps
- **[How It Works](guides/how-it-works.md)** — Technical overview
- **[Architecture](architecture/architecture.md)** — Detailed design and modules
- **[Development](architecture/development.md)** — Development setup and workflow
- **[Contributing](contribute/guidelines.md)** — Contribution guidelines
- **[Roadmap](contribute/roadmap.md)** — Future improvements

## 🏗️ Architecture Overview

```
User Interface (CLI, GUI, Batch)
        ↓
Scanning Engine (hash matching, recursion)
        ↓
Support Services (API, scheduler, reports)
        ↓
Data Layer (JSON configs, quarantine)
```

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Core code** | ~500 lines Python |
| **Tests** | 18 unit tests |
| **CI/CD** | 12 test matrices |
| **Compatibility** | Python 3.9, 3.10, 3.11, 3.12 |
| **OS Support** | Windows, macOS, Linux |
| **Dependencies** | 2 (colorama, requests) |
| **Documentation** | 1200+ lines |

## 🔧 Components

### Core Scanning (`Virus_project.py`)
- SHA256 file hashing
- Signature database loading
- Recursive directory scanning
- Exclusion pattern matching
- Malware quarantine

### User Interfaces
- **CLI** — Command-line interface
- **GUI** — Tkinter-based graphical interface
- **Scheduler** — Background automated scanning
- **Batch** — Programmatic scanning

### Integration & Reporting
- **VirusTotal API** — External threat intelligence
- **Report Generator** — HTML & JSON export
- **Logging** — Audit trails and debugging

## 🧪 Testing

```bash
# Run all tests
python -m unittest test_virus_project -v

# Run with coverage
pytest test_virus_project.py --cov=. --cov-report=html
```

**CI/CD**: Tests automatically run on every push across:
- Ubuntu (latest)
- macOS (latest)
- Windows (latest)
- Python 3.9, 3.10, 3.11, 3.12

## 📦 Distribution

### Development
```bash
pip install -e .
```

### PyPI Package
Installable via pip, ready for distribution.

### Standalone Executable
Compiled Windows executable (no Python required).

### Docker
Containerized deployment.

## 🤝 Contributing

We welcome contributions! Before submitting:

1. Read [Contributing Guidelines](contribute/guidelines.md)
2. Check [Project Structure](contribute/structure.md)
3. Run tests: `python -m unittest test_virus_project -v`
4. Format code: `black .`

## 🗺️ Roadmap

Short term:
- Web UI (Flask/FastAPI + React)
- Database backend (SQLite/PostgreSQL)
- YARA rules integration

Medium term:
- ML-based detection
- Real-time file monitoring
- REST API server

Long term:
- Distributed scanning
- Advanced threat feeds
- Kubernetes deployment

See [full roadmap](contribute/roadmap.md).

## 📝 License

MIT License — See LICENSE file for details.

## 👤 Author

[Nelson M Madeira Rijo](https://github.com/Nekas1980)  
*Python Bootcamp — IEFP 2026 · Transition to Cybersecurity* 🔐

---

**Get started**: [Installation Guide →](guides/installation.md)
