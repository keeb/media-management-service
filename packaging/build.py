#!/usr/bin/env python3
"""
Build script for creating the mms single binary using PyInstaller.

Usage:
    python packaging/build.py
    # or via uv:
    uv run python packaging/build.py
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    # Get paths
    project_root = Path(__file__).parent.parent
    spec_file = project_root / "packaging" / "pyinstaller.spec"
    dist_dir = project_root / "dist"

    print(f"Project root: {project_root}")
    print(f"Spec file: {spec_file}")
    print(f"Output directory: {dist_dir}")

    # Verify spec file exists
    if not spec_file.exists():
        print(f"Error: Spec file not found at {spec_file}")
        sys.exit(1)

    # Run PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file),
    ]

    print(f"\nRunning: {' '.join(cmd)}")
    print("-" * 60)

    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode != 0:
        print(f"\nBuild failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    # Verify output
    binary_path = dist_dir / "mms"
    if binary_path.exists():
        size_mb = binary_path.stat().st_size / (1024 * 1024)
        print("-" * 60)
        print(f"\nBuild successful!")
        print(f"Binary: {binary_path}")
        print(f"Size: {size_mb:.1f} MB")
        print(f"\nTest with: {binary_path} --help")
    else:
        print(f"\nWarning: Expected binary not found at {binary_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
