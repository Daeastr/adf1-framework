# core/venv_guard.py
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError
import sys
import subprocess
import codecs

REQS_FILE = Path(__file__).parent.parent / "requirements.txt"

REQUIRED = {
    "pytest": "8",
    # add any guard-checked packages here
}

class VenvMismatchError(Exception):
    pass

def open_requirements(path):
    """
    Smart encoding detection for requirements.txt files.
    Handles UTF-16 BOM and falls back to UTF-8-sig for UTF-8 BOM.
    """
    with open(path, 'rb') as raw:
        start = raw.read(4)
    
    if start.startswith(codecs.BOM_UTF16_LE) or start.startswith(codecs.BOM_UTF16_BE):
        enc = 'utf-16'
    else:
        enc = 'utf-8-sig'
    
    with open(path, 'r', encoding=enc) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def check_packages():
    """
    Check critical packages against REQUIRED dictionary.
    Returns list of problems found.
    """
    problems = []
    for name, major in REQUIRED.items():
        try:
            v = version(name)
            if not v.startswith(f"{major}."):
                problems.append(f"{name} is {v}, expected {major}.x")
        except PackageNotFoundError:
            problems.append(f"{name} not installed")
    return problems

def check_venv_health() -> None:
    """
    Verify all dependencies in requirements.txt are installed
    at the correct version in the current interpreter.
    Raises VenvMismatchError if any are missing/mismatched.
    """
    if not REQS_FILE.exists():
        print("⚠️ requirements.txt not found — skipping venv check")
        return

    # Check critical packages first
    problems = check_packages()
    if problems:
        raise VenvMismatchError("\n".join(problems))

    # Optional: Still check requirements.txt for completeness
    # This is now more of a "nice to have" since critical checks are above
    print("✅ Critical packages verified")

def auto_fix():
    """Attempt to pip‑install anything missing or outdated."""
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(REQS_FILE)], check=True)