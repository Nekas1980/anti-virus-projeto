# 📦 Packaging & Distribution Guide

This document explains how to build and distribute Antivírus Projeto for different platforms.

## Prerequisites

```bash
# Install packaging tools
pip install build wheel setuptools twine pyinstaller
```

---

## 1. Development Installation (Local Testing)

```bash
# Install in editable mode (for development)
pip install -e .

# Includes CLI commands:
antivirus-scan /path/to/scan
antivirus-scheduler
antivirus-update
```

---

## 2. PyPI Distribution (pip install antivirus-projeto)

### Build distribution packages

```bash
# Clean previous builds
rm -rf build dist *.egg-info

# Build wheel and source distribution
python -m build

# Output: dist/antivirus_projeto-1.0.0.tar.gz (source)
#         dist/antivirus_projeto-1.0.0-py3-none-any.whl (wheel)
```

### Upload to PyPI (requires PyPI account & credentials)

```bash
# Test upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install -i https://test.pypi.org/simple/ antivirus-projeto

# Production upload to PyPI
python -m twine upload dist/*
```

### Users can then install with:

```bash
pip install antivirus-projeto
antivirus-scan ~/Downloads
```

---

## 3. Standalone Executables (PyInstaller)

### Windows (.exe)

```bash
# On Windows machine
pyinstaller build_exe.spec

# Output: dist/antivirus_projeto.exe
# Users can run without Python installed:
antivirus_projeto.exe C:\Users\Downloads
```

### macOS/Linux

```bash
# Build native executable
pyinstaller build_exe.spec

# Output: dist/antivirus_projeto (executable)
chmod +x dist/antivirus_projeto
./dist/antivirus_projeto ~/Downloads
```

### Compression for distribution

```bash
# Windows
cd dist
7z a antivirus_projeto_win_x64.zip antivirus_projeto.exe exclusions.json signatures.json

# macOS
cd dist
zip -r antivirus_projeto_macos.zip antivirus_projeto

# Linux
cd dist
tar -czf antivirus_projeto_linux_x64.tar.gz antivirus_projeto
```

---

## 4. GitHub Releases

### Create release artifacts manually

```bash
# 1. Tag the release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 2. Build all packages
python -m build
pyinstaller build_exe.spec

# 3. Create dist/ structure for upload
mkdir releases/v1.0.0
cp dist/antivirus_projeto-1.0.0* releases/v1.0.0/
cp dist/antivirus_projeto releases/v1.0.0/antivirus_projeto_linux
```

### Upload via GitHub CLI

```bash
gh release create v1.0.0 \
  releases/v1.0.0/antivirus_projeto-1.0.0-py3-none-any.whl \
  releases/v1.0.0/antivirus_projeto-1.0.0.tar.gz \
  releases/v1.0.0/antivirus_projeto_linux \
  --title "Antivírus Projeto v1.0.0" \
  --notes "Release notes here"
```

---

## 5. Docker Distribution (Optional)

### Create Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["python", "Virus_project.py"]
```

### Build and publish

```bash
docker build -t nekas1980/antivirus-projeto:1.0.0 .
docker push nekas1980/antivirus-projeto:1.0.0
```

---

## Comparison of Distribution Methods

| Method | Users Can Run | Requires Python | Download Size | Installation Time | Easiest For |
|--------|--------------|-----------------|----------------|-------------------|------------|
| `pip install` | ✅ Any system | ✅ Yes | Small (~50KB) | ~30s | Developers |
| Standalone .exe | ✅ Windows only | ❌ No | Large (~50MB) | Quick | Non-technical |
| Standalone binary | ✅ macOS/Linux | ❌ No | Large (~50MB) | Quick | Non-technical |
| Docker | ✅ Any (with Docker) | ❌ No (containerized) | Large (~500MB) | 1-2 min | DevOps |
| Source (git clone) | ✅ Any system | ✅ Yes | Medium (~1MB) | ~2 min | Contributors |

---

## Current Project Status

🔴 **NOT production-ready** — This is an educational project demonstrating malware scanning concepts.

### For production use:
- [ ] Security audit by external expert
- [ ] Heuristic analysis engine (not just signatures)
- [ ] Real-time protection (file system monitoring)
- [ ] Machine learning detection models
- [ ] Automated threat intelligence feeds
- [ ] Formal testing and certification
- [ ] Professional support/SLA

### Current limitations:
- Signature-based detection only (no heuristics)
- Manual database updates required
- No real-time scanning
- Limited to hash matching
- Educational use only

---

## Troubleshooting

### PyInstaller: "module not found"
```bash
# Add hidden imports to build_exe.spec
# hiddenimports=[..., "your_module", ...]
```

### PyPI: "Authentication failed"
```bash
# Create ~/.pypirc or use token
# python -m twine upload --verbose dist/*
```

### File size too large
```bash
# Exclude unnecessary data from build_exe.spec:
excludedimports=["tkinter"]  # if not using GUI
```

---

## Next Steps

1. ✅ Test locally: `pip install -e .`
2. ✅ Build packages: `python -m build`
3. ⏳ Publish to PyPI (requires authentication)
4. ⏳ Create GitHub releases with artifacts
5. ⏳ (Optional) Set up CI/CD for automated releases
