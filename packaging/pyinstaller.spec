# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for building the mms single binary.

This spec file bundles:
- The mediaservice package and all CLI commands
- The prompts directory as data files
- All Python dependencies

Usage:
    pyinstaller --clean --noconfirm build/pyinstaller.spec
    # or via build script:
    python build/build.py
"""

import os
from pathlib import Path

# Get absolute paths
project_root = Path(SPECPATH).parent
prompts_dir = project_root / "prompts"
python_src = project_root / "python" / "src"

# Verify prompts directory exists
if not prompts_dir.exists():
    raise FileNotFoundError(f"Prompts directory not found: {prompts_dir}")

block_cipher = None

a = Analysis(
    [str(python_src / "mediaservice" / "cli" / "main.py")],
    pathex=[str(python_src)],
    binaries=[],
    datas=[
        # Bundle prompts directory
        (str(prompts_dir), "prompts"),
    ],
    hiddenimports=[
        # Ensure all CLI modules are included
        "mediaservice.cli.cleaner",
        "mediaservice.cli.media_worker",
        "mediaservice.cli.subsplease_dl",
        "mediaservice.cli.erai_raws_dl",
        "mediaservice.cli.indexer",
        "mediaservice.cli.sg_worker",
        "mediaservice.cli.sg_scrape",
        # Core modules
        "mediaservice.db.mongo",
        "mediaservice.db.indexer",
        "mediaservice.download.images",
        "mediaservice.download.transmission",
        "mediaservice.organize.mover",
        "mediaservice.organize.parse",
        "mediaservice.organize.classify",
        "mediaservice.organize.filter",
        "mediaservice.sources.subsplease",
        "mediaservice.sources.erai_raws",
        "mediaservice.util.file",
        "mediaservice.util.ollama",
        # Dependencies that might need explicit inclusion
        "click",
        "pymongo",
        "requests",
        "flask",
        "flask_cors",
        "yaml",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        "tkinter",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "PIL",
        "cv2",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="mms",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
