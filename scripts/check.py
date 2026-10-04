"""Required CPU checks; missing tooling is an error, never a silent skip."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    for args in (
        ("ruff", "check", "src", "scripts", "deploy", "tests"),
        ("unittest", "discover", "-s", "tests", "-v"),
    ):
        subprocess.run([sys.executable, "-m", *args], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
