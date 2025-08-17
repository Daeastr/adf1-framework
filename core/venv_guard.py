from pathlib import Path
import pkg_resources
import sys
import subprocess

REQS_FILE = Path(__file__).parent.parent / "requirements.txt"

class VenvMismatchError(Exception):
    pass

def check_venv_health() -> None:
    """
    Verify all dependencies in requirements.txt are installed
    at the correct version in the current interpreter.
    Raises VenvMismatchError if any are missing/mismatched.
    """
    if not REQS_FILE.exists():
        print("⚠️ requirements.txt not found — skipping venv check")
        return

    with open(REQS_FILE, "r", encoding="utf-8") as f:
        required = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    try:
        pkg_resources.require(required)
    except pkg_resources.ResolutionError as e:
        raise VenvMismatchError(str(e))

def auto_fix():
    """Attempt to pip‑install anything missing or outdated."""
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(REQS_FILE)], check=True)
