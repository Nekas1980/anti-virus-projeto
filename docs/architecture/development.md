# 🛠️ Development Guide

Complete guide for setting up a development environment, running tests, and building the project locally.

---

## 📋 Prerequisites

- **Python**: 3.9 or later
- **Git**: For version control
- **pip/venv**: Python package management

### Verify Prerequisites

```bash
python3 --version          # Should be 3.9+
python3 -m pip --version   # pip version
git --version              # git version
```

---

## 🚀 Initial Setup

### 1. Clone the Repository

```bash
# Clone via HTTPS (recommended)
git clone https://github.com/Nekas1980/anti-virus-projeto.git
cd anti-virus-projeto

# Or clone via SSH (if you have SSH keys configured)
git clone git@github.com:Nekas1980/anti-virus-projeto.git
cd anti-virus-projeto
```

### 2. Create Virtual Environment

```bash
# Create venv (recommended to isolate dependencies)
python3 -m venv venv

# Activate venv
source venv/bin/activate      # macOS/Linux
# or
venv\Scripts\activate          # Windows
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install development tools (optional but recommended)
pip install -e ".[dev]"
```

This installs:
- Main dependencies: `colorama`, `requests`
- Dev tools: `pytest`, `pytest-cov`, `black`, `flake8`, `mypy`

---

## 🎯 Common Development Tasks

### Running the Application

```bash
# CLI mode
python Virus_project.py

# GUI mode (simple)
python gui.py

# GUI mode (advanced)
python gui3.py

# Scheduler (background scanning)
python scheduler.py create-config
python scheduler.py run

# Update signatures from VirusTotal
export VIRUSTOTAL_API_KEY="your_key_here"
python virustotal_updater.py
```

### Running Tests

```bash
# Run all tests
python -m unittest test_virus_project -v

# Run specific test class
python -m unittest test_virus_project.TestSHA256File -v

# Run specific test method
python -m unittest test_virus_project.TestSHA256File.test_sha256_valid_file -v

# Run with coverage report (requires pytest-cov)
pytest test_virus_project.py --cov=. --cov-report=html
# Opens coverage/index.html in browser
```

### Code Quality Checks

```bash
# Format code (auto-fix style issues)
black .

# Check code style (without changes)
black --check .

# Lint for errors
flake8 .

# Type checking
mypy Virus_project.py

# Quick style check
python -m py_compile *.py
```

---

## 📂 Project Structure

```
anti-virus-projeto/
├── Virus_project.py           # Core engine (main entry point)
├── gui.py                     # Tkinter GUI (simple version)
├── gui2.py                    # GUI v2 (with threading)
├── gui3.py                    # GUI v3 (advanced - recommended)
├── report_generator.py        # HTML/JSON report generation
├── scheduler.py               # Background task scheduling
├── virustotal_updater.py      # Threat intelligence API
├── test_virus_project.py      # Unit tests (18 tests)
├── requirements.txt           # Python dependencies
├── setup.py                   # PyPI packaging configuration
├── pyproject.toml            # Modern Python project config
├── build_exe.spec            # PyInstaller configuration
├── signatures.json           # Malware hash database (local)
├── exclusions.json           # Directory exclusion patterns
├── schedule_config.json      # Scheduler configuration (generated)
├── README.md                 # User documentation
├── ARCHITECTURE.md           # Technical design document
├── CONTRIBUTING.md           # Contribution guidelines
├── DEVELOPMENT.md            # This file
├── BUILD_INSTRUCTIONS.md     # Distribution & packaging guide
├── .github/
│   └── workflows/
│       └── tests.yml         # GitHub Actions CI/CD
├── output/                   # Generated reports (created on run)
├── quarantine/              # Isolated infected files (created on run)
├── scheduled_reports/       # Timestamped scan reports (created on scheduler run)
└── .git/                    # Git repository metadata
```

---

## 🔄 Git Workflow

### Creating a Feature Branch

```bash
# Update main from upstream
git fetch origin
git checkout main
git merge origin/main

# Create new feature branch
git checkout -b feature/my-feature
```

### Making Changes

```bash
# Edit files...

# Check what changed
git status

# Stage changes
git add file1.py file2.py

# Commit with clear message
git commit -m "feat: add new scanning capability

Explain why this change was made and what it does.
Can reference issues: Fixes #42"
```

### Pushing Changes

```bash
# Push to your fork (if you're a contributor)
git push origin feature/my-feature

# Then open a Pull Request on GitHub
```

### Keeping Your Branch Updated

```bash
# If main moved ahead while you were working:
git fetch origin
git rebase origin/main

# Or merge (if you prefer)
git merge origin/main
```

### Syncing Your Fork (Contributors)

```bash
# Add upstream remote (one-time)
git remote add upstream https://github.com/Nekas1980/anti-virus-projeto.git

# Update your local main
git fetch upstream
git checkout main
git rebase upstream/main

# Update your fork on GitHub
git push origin main
```

---

## 🧪 Testing Best Practices

### Writing Tests

```python
import unittest
from Virus_project import sha256_file, load_signatures

class TestNewFeature(unittest.TestCase):
    """Test description."""
    
    def test_something(self):
        """Test specific behavior."""
        result = some_function(input_value)
        self.assertEqual(result, expected_value)
    
    def test_error_case(self):
        """Test error handling."""
        result = some_function(invalid_input)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
```

### Test Organization

```
test_virus_project.py:
├── TestSHA256File         # Tests for sha256_file()
├── TestLoadSignatures     # Tests for load_signatures()
├── TestLoadExclusions     # Tests for load_exclusions()
├── TestShouldSkipPath     # Tests for should_skip_path()
├── TestScanFile           # Tests for scan_file()
├── TestAddSignature       # Tests for add_signature()
└── TestScanResult         # Tests for ScanResult dataclass
```

### Running Tests Before Commit

```bash
# Always run tests before pushing
python -m unittest test_virus_project -v

# If all green, commit:
git commit -m "..."
git push origin feature/branch-name
```

---

## 🐛 Debugging

### Enabling Verbose Logging

All modules use Python's `logging` module configured to output to both console and files.

```python
# Logging configuration in each module:
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detail
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scan.log"),
        logging.StreamHandler(),
    ],
)
```

### Using Print Debugging

```python
# For quick debugging (use sparingly)
print(f"DEBUG: variable = {variable}")

# Better: use logging
logger.debug(f"variable = {variable}")
```

### Interactive Debugging

```python
# Using pdb (Python Debugger)
import pdb

# In your code, add breakpoint:
pdb.set_trace()  # Execution pauses here
# Commands: n (next), c (continue), l (list), p var (print variable)
```

### Checking File Hashes

```bash
# Verify a file's SHA256 locally
python -c "from Virus_project import sha256_file; from pathlib import Path; print(sha256_file(Path('test.txt')))"

# Compare with VirusTotal
export VIRUSTOTAL_API_KEY="..."
python virustotal_updater.py
# Then query by hash
```

---

## 🔧 Configuration Files

### `signatures.json`

```json
{
  "malware_hashes": {
    "a1b2c3d4e5f6...": "Trojan.Generic",
    "f6e5d4c3b2a1...": "Win32.Virus"
  }
}
```

**Modify**: When adding test malware signatures
```bash
python -c "
import json
from pathlib import Path

sigs = json.loads(Path('signatures.json').read_text())
sigs['malware_hashes']['newhash123'] = 'Test.Trojan'
Path('signatures.json').write_text(json.dumps(sigs, indent=2))
"
```

### `exclusions.json`

```json
{
  "exclusion_patterns": [
    "node_modules",
    ".git",
    "*.tmp"
  ]
}
```

**Modify**: Add patterns to skip
```bash
# Edit directly or use:
python -c "
import json
from pathlib import Path

excl = json.loads(Path('exclusions.json').read_text())
excl['exclusion_patterns'].append('mynewpattern')
Path('exclusions.json').write_text(json.dumps(excl, indent=2))
"
```

### `schedule_config.json`

```json
{
  "enabled": true,
  "auto_quarantine": false,
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

**Generate**: `python scheduler.py create-config`
**Modify**: Edit JSON directly, then run `python scheduler.py run`

---

## 📦 Building Distributions

### Local Testing Before Release

```bash
# Test PyPI installation locally
pip install -e .

# Verify CLI commands work
antivirus-scan /tmp
antivirus-update --help
antivirus-scheduler --help

# Test building packages
python -m build

# Check package contents
tar -tzf dist/antivirus_projeto-1.0.0.tar.gz | head -20
unzip -l dist/antivirus_projeto-1.0.0-py3-none-any.whl | head -20
```

### Creating Standalone Executable (Windows)

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller build_exe.spec

# Result: dist/antivirus_projeto.exe
# Test it:
.\dist\antivirus_projeto.exe C:\Users\Downloads
```

---

## 🚨 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'colorama'"

```bash
# Solution: Install requirements
pip install -r requirements.txt
# Or
pip install colorama requests
```

### Issue: Tests fail with "cannot import Virus_project"

```bash
# Solution: Run from project root
cd /path/to/anti-virus-projeto
python -m unittest test_virus_project -v
```

### Issue: GUI doesn't open

```bash
# Check if tkinter is installed (comes with Python)
python -c "import tkinter; print('OK')"

# On Linux, might need system package:
sudo apt-get install python3-tk  # Debian/Ubuntu
brew install python-tk@3.11       # macOS (if not included)
```

### Issue: "Permission denied" on macOS/Linux scripts

```bash
# Make script executable
chmod +x scheduler.py
chmod +x Virus_project.py

# Then run
./Virus_project.py /path/to/scan
```

### Issue: JSON parsing error in configurations

```bash
# Validate JSON syntax
python -m json.tool signatures.json
python -m json.tool exclusions.json
python -m json.tool schedule_config.json

# Fix: Use proper JSON format (quotes around strings, no trailing commas)
```

---

## 📊 Performance Profiling

### Measuring Scan Time

```python
import time
from pathlib import Path
from Virus_project import scan_directory, load_signatures, load_exclusions

start = time.time()
results = scan_directory(
    Path("/path/to/scan"),
    load_signatures(Path("signatures.json")),
    load_exclusions(Path("exclusions.json"))
)
elapsed = time.time() - start

print(f"Scanned {len(results)} files in {elapsed:.2f} seconds")
print(f"Speed: {len(results)/elapsed:.0f} files/sec")
```

### Memory Usage

```bash
# Monitor memory while running
python -m memory_profiler Virus_project.py /path

# Or use system monitoring
time python Virus_project.py /path
```

---

## 🔐 Security Considerations for Development

### API Key Management

```bash
# NEVER commit API keys
# Always use environment variables
export VIRUSTOTAL_API_KEY="abc123def456"
python virustotal_updater.py

# Add to .gitignore:
# .env
# *.key
# secrets.json
```

### Safe Testing with Real Files

```bash
# Create test directory with harmless files
mkdir -p test_files
echo "clean content" > test_files/clean.txt

# Never test with actual malware unless in isolated environment
# For learning, use known-safe files with hashes in signatures.json
```

---

## 🎓 Learning Resources

Within this project:
- **ARCHITECTURE.md** — Design and data flow explanations
- **CONTRIBUTING.md** — Contribution workflow and guidelines
- **README.md** — User-facing documentation

External:
- [Python Docs](https://docs.python.org/3)
- [unittest tutorial](https://docs.python.org/3/library/unittest.html)
- [pathlib guide](https://docs.python.org/3/library/pathlib.html)

---

## 📝 Development Checklist

Before pushing code:

- [ ] Changes address the issue/feature
- [ ] Code follows PEP 8 (run `black .`)
- [ ] No obvious bugs (run `flake8 .`)
- [ ] All tests pass: `python -m unittest test_virus_project -v`
- [ ] New tests written for new functionality
- [ ] Documentation updated (README, ARCHITECTURE, etc.)
- [ ] No API keys or secrets in commits
- [ ] Git history is clean (meaningful commit messages)
- [ ] Tested across platforms if possible (macOS, Linux, Windows)

---

## 💬 Getting Help

- **GitHub Issues**: https://github.com/Nekas1980/anti-virus-projeto/issues
- **GitHub Discussions**: https://github.com/Nekas1980/anti-virus-projeto/discussions
- **CONTRIBUTING.md**: Contribution guidelines and workflow

---

**Happy coding! 🚀**
