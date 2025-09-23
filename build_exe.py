#!/usr/bin/env python3
"""Build a standalone Goal Manager executable using PyInstaller."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

try:
    from PyInstaller import __main__ as pyinstaller_main
except ModuleNotFoundError:  # pragma: no cover - handled at runtime
    pyinstaller_main = None


def main() -> None:
    if pyinstaller_main is None:
        print("PyInstaller is required. Install it with 'pip install pyinstaller'.")
        sys.exit(1)

    project_root = Path(__file__).resolve().parent
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

    # Clean previous build artifacts to avoid confusing results.
    if build_dir.exists():
        shutil.rmtree(build_dir)
    dist_dir.mkdir(exist_ok=True)
    exe_name = "GoalManager.exe" if sys.platform.startswith("win") else "GoalManager"
    existing_binary = dist_dir / exe_name
    if existing_binary.exists():
        existing_binary.unlink()

    print("Building Goal Manager executable with PyInstaller…")
    pyinstaller_main.run(
        [
            "--name=GoalManager",
            "--onefile",
            "--console",
            "--distpath",
            str(dist_dir),
            "--workpath",
            str(build_dir),
            str(project_root / "goal_manager.py"),
        ]
    )

    output_path = dist_dir / exe_name
    if output_path.exists():
        print(f"Executable created at: {output_path}")
    else:
        print(
            "PyInstaller finished but the expected executable was not found. "
            "Check the PyInstaller output above for details."
        )


if __name__ == "__main__":
    main()
