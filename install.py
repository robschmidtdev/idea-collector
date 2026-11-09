#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT_DIR = ROOT / "idea_collector"
VENV_DIR = ROOT / "venv"


def main() -> int:
    if sys.platform == "nt":
        python = VENV_DIR / "Scripts" / "python.exe"
    else:
        python = VENV_DIR / "bin" / "python"

    if not python.exists():
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or not python.exists():
            print("Could not create the virtual environment.", file=sys.stderr)
            return 1

    install = subprocess.run(
        [str(python), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if install.returncode != 0:
        print("Could not install the Python requirements.", file=sys.stderr)
        print(install.stdout + install.stderr)
        return 1

    migrate = subprocess.run(
        [str(python), "manage.py", "migrate"],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
        check=False,
    )
    if migrate.returncode != 0:
        print("Database migration failed.\n\n" + migrate.stdout + migrate.stderr, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
