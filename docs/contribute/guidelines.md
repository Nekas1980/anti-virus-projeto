# 🤝 Contributing to Antivírus Projeto

Thank you for your interest in contributing! This is an **educational project** designed to teach cybersecurity fundamentals. All contributions help improve the learning experience for students and developers.

## ⚠️ Important Disclaimer

**This project is for EDUCATIONAL PURPOSES ONLY.** It is NOT production-ready and should NOT be used as a primary antivirus solution. It demonstrates basic malware scanning concepts and is intended for learning, not real-world protection.

---

## 🎯 How to Contribute

### 1. Report Issues

Found a bug or have a suggestion?

1. Check if the issue already exists: https://github.com/Nekas1980/anti-virus-projeto/issues
2. Create a new issue with:
   - Clear title describing the problem
   - Steps to reproduce (if it's a bug)
   - Expected behavior vs actual behavior
   - Python version, OS, and relevant environment details
   - Screenshots or error logs (if applicable)

### 2. Propose Features

Educational improvements are welcome! Before coding, open a discussion:

1. Explain the learning objective: "This feature teaches students about..."
2. Describe the implementation approach
3. Link to relevant security/Python concepts
4. Discuss with maintainers before starting

### 3. Submit Code Changes

#### Fork and Clone

```bash
# 1. Fork on GitHub (button in top-right)
# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/anti-virus-projeto.git
cd anti-virus-projeto

# 3. Add upstream remote
git remote add upstream https://github.com/Nekas1980/anti-virus-projeto.git
```

#### Create a Feature Branch

```bash
# Update main
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/what-you-add
# or
git checkout -b fix/what-you-fix
```

#### Make Your Changes

```bash
# 1. Code your changes
# 2. Run tests
python -m unittest test_virus_project -v

# 3. Check code style
python -m black --check .
python -m flake8 .

# 4. If style issues, auto-fix with:
python -m black .
```

#### Commit and Push

```bash
# Commit with clear message
git commit -m "Type: Short description

Longer explanation of why this change is needed and what it does.
Reference issue #123 if applicable."

# Commit types:
# feat: New feature
# fix: Bug fix
# docs: Documentation only
# refactor: Code restructuring (no feature change)
# test: Test additions/modifications
# ci: CI/CD configuration
# chore: Maintenance tasks

# Push to your fork
git push origin feature/what-you-add
```

#### Open a Pull Request

1. Go to https://github.com/Nekas1980/anti-virus-projeto/pulls
2. Click "New Pull Request"
3. Select: `Nekas1980/anti-virus-projeto:main` ← `YourUsername/anti-virus-projeto:feature/name`
4. Write a clear PR description:
   - What problem does this solve?
   - How does it improve the educational value?
   - Which learning objectives does it address?
5. Reference related issues: "Fixes #123"

---

## 📋 Contribution Guidelines

### Code Quality

- **Python version**: 3.9+ (test with 3.9, 3.10, 3.11, 3.12)
- **Style**: Follow PEP 8, use `black` and `flake8`
- **Type hints**: Add type annotations to function parameters and returns
- **Comments**: Only for "WHY" not "WHAT" — code should be self-explanatory
- **No magic numbers**: Use named constants

### Testing

- **Write tests** for new functions using Python's `unittest`
- **Run the full test suite**: `python -m unittest test_virus_project -v`
- **Aim for > 80% coverage** on new code
- **Test across platforms**: macOS, Linux, Windows (CI/CD handles this)

### Documentation

- **Update README.md** if you add user-facing features
- **Add docstrings** to public functions (one-line summary)
- **Update ARCHITECTURE.md** if you change module structure
- **Add examples** if introducing new concepts

### Educational Value

This project teaches:
- SHA256 hashing and file integrity
- Pattern matching and configuration (fnmatch, JSON)
- File system traversal and filtering
- External API integration (VirusTotal)
- Task scheduling and background execution
- Report generation (HTML, JSON)
- Unit testing and CI/CD
- GUI development with Tkinter
- Logging and error handling

**New contributions should reinforce these concepts.** Avoid:
- Production-grade features (encryption, compression, complex caching)
- Heuristic analysis (too complex for learning phase)
- Real-time monitoring (architectural complexity)
- Dependencies on heavy external services

---

## 🧪 Local Development Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install in editable mode + dev tools
pip install -e ".[dev]"

# 3. Verify setup
python -m unittest test_virus_project -v

# 4. Format and lint
black .
flake8 .
```

---

## 📁 Project Structure

```
anti-virus-projeto/
├── Virus_project.py       # Core scanning engine
├── gui.py                 # Tkinter GUI (simple)
├── report_generator.py    # HTML/JSON report generation
├── scheduler.py           # Scheduled scanning
├── virustotal_updater.py  # VirusTotal API integration
├── test_virus_project.py  # Unit tests (18 tests)
├── signatures.json        # Malware hash database
├── exclusions.json        # Directory exclusion patterns
├── requirements.txt       # Python dependencies
├── setup.py              # PyPI packaging
├── pyproject.toml        # Modern Python packaging
├── BUILD_INSTRUCTIONS.md # Distribution guide
├── ARCHITECTURE.md       # Technical architecture
├── DEVELOPMENT.md        # Development setup
└── .github/workflows/    # GitHub Actions CI/CD
    └── tests.yml         # Automated testing
```

---

## 🚀 Review Process

1. **Automated checks**: GitHub Actions runs tests on all platforms/Python versions
2. **Code review**: Maintainers check:
   - Code quality and clarity
   - Educational value
   - Test coverage
   - Documentation completeness
3. **Feedback**: Maintainers request changes if needed
4. **Merge**: Once approved, changes are merged to main

---

## 💡 Ideas for Contributions

### Easy (Good for First-Time Contributors)
- [ ] Add more unit tests (aim for 100% coverage)
- [ ] Improve error messages
- [ ] Add examples to documentation
- [ ] Create tutorial walkthroughs
- [ ] Translate comments to English/other languages

### Medium
- [ ] Add support for more file types (PE files, ZIP inspection)
- [ ] Create additional GUI layouts (wxPython, PyQt examples)
- [ ] Implement custom report templates
- [ ] Add benchmark/performance tests
- [ ] Create educational labs with sample files

### Advanced
- [ ] Implement basic pattern/behavior heuristics (with caveats about limitations)
- [ ] Add machine learning module (classification of benign vs. suspicious patterns)
- [ ] Create REST API server (Flask/FastAPI)
- [ ] Implement database backend (SQLite, PostgreSQL)
- [ ] Create Jupyter notebooks for interactive learning

---

## 📚 Resources

- [Python 3.9+ Docs](https://docs.python.org/3.9/)
- [SHA256 in Python](https://docs.python.org/3/library/hashlib.html)
- [Pathlib Module](https://docs.python.org/3/library/pathlib.html)
- [Unit Testing](https://docs.python.org/3/library/unittest.html)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)

---

## ❓ Questions?

- Open a GitHub Discussion: https://github.com/Nekas1980/anti-virus-projeto/discussions
- Check existing Issues/PRs for similar questions
- Read DEVELOPMENT.md for setup help

---

## 📜 License

By contributing, you agree that your contributions are licensed under the MIT License. See LICENSE file for details.

---

**Thank you for helping make this educational project better!** 🙏
