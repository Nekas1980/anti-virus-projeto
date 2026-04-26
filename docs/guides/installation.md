# Installation

Complete setup guide for development and usage.

## Prerequisites

- **Python**: 3.9 or later
- **Git**: For version control
- **pip/venv**: Python package management (built-in)

### Verify Prerequisites

```bash
python3 --version          # Should be 3.9+
python3 -m pip --version   # pip version
git --version              # git version
```

## Installation Steps

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
# Create isolated Python environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Or activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip to latest
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Install development tools (optional but recommended)
pip install -e ".[dev]"
```

This installs:
- **Runtime**: `colorama` (colored terminal output), `requests` (HTTP library)
- **Development**: `pytest`, `pytest-cov`, `black`, `flake8`, `mypy`

## Verify Installation

```bash
# Check if scanner works
python Virus_project.py --help

# Run tests to verify everything works
python -m unittest test_virus_project -v
```

Expected output: All 18 tests pass ✅

## Distribution Installation

### Via pip (if published)

```bash
pip install antivirus-projeto
```

### From source (editable mode)

```bash
pip install -e .
```

This creates CLI shortcuts:
- `antivirus-scan` — Run scanner
- `antivirus-scheduler` — Run scheduler
- `antivirus-update` — Update signatures

## Next Steps

- [Quick Start](quickstart.md) — Run your first scan
- [How It Works](how-it-works.md) — Understand the technology
- [Development](../architecture/development.md) — Setup for development
