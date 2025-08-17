#!/usr/bin/env python3
"""Launcher that runs a target script using the repo's venv python when available.

Usage: python scripts/run_sync_action_map.py [path/to/script.py]
If a venv exists in the repo (./venv or ./.venv), this will re-exec using that
interpreter. Otherwise it will run the target script in-process.
"""
import os
import sys
import subprocess
from pathlib import Path


def find_repo_venv_python(repo_root: Path):
    candidates = [
        repo_root / "venv" / "Scripts" / "python.exe",
        repo_root / "venv" / "bin" / "python",
        repo_root / ".venv" / "Scripts" / "python.exe",
        repo_root / ".venv" / "bin" / "python",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def main():
    repo_root = Path(__file__).resolve().parents[1]
    # Default target is the sync_action_map script
    if len(sys.argv) > 1:
        target = Path(sys.argv[1]).resolve()
    else:
        target = repo_root / "scripts" / "sync_action_map.py"

    # If a VIRTUAL_ENV is active and points into the repo, prefer it
    venv_python = None
    venv_env = os.environ.get("VIRTUAL_ENV")
    if venv_env:
        candidate = Path(venv_env) / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
        if candidate.exists():
            venv_python = str(candidate)

    # Otherwise, look for common repo venv locations
    if not venv_python:
        venv_python = find_repo_venv_python(repo_root)

    # If we found a repo venv python and it's not the current interpreter, exec it
    try:
        current = Path(sys.executable).resolve()
    except Exception:
        current = None

    if venv_python:
        try:
            vpath = Path(venv_python).resolve()
            if current is None or vpath != current:
                # Re-exec using the venv python to ensure correct deps
                rc = subprocess.call([str(vpath), str(target)])
                sys.exit(rc if isinstance(rc, int) else 0)
        except Exception:
            # Fallback to running in-process
            pass

    # Run target script in-process to avoid extra process spawn
    sys.path.insert(0, str(repo_root))
    import runpy
    try:
        runpy.run_path(str(target), run_name="__main__")
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 0
        sys.exit(code)
    except Exception as e:
        print(f"Error while running {target}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
