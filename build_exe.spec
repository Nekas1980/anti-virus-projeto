# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Antivírus Projeto.

Usage: pyinstaller build_exe.spec
Creates standalone executable in dist/

Windows: antivirus_projeto.exe
Linux/macOS: antivirus_projeto
"""

from PyInstaller.utils.hooks import collect_submodules
import sys
from pathlib import Path

project_root = Path(SPECPATH)

a = Analysis(
    [str(project_root / "Virus_project.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / "signatures.json"), "."),
        (str(project_root / "exclusions.json"), "."),
    ],
    hiddenimports=[
        "colorama",
        "requests",
        "pathlib",
        "json",
        "hashlib",
        "logging",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="antivirus_projeto",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
