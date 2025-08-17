#!/usr/bin/env python3
"""Lint instructions folder: ensure each .json is valid JSON and contains id/action/params."""
import json
from pathlib import Path
import sys

INSTR = Path(__file__).resolve().parents[1] / "instructions"
if not INSTR.exists():
    print("No instructions folder found; skipping.")
    sys.exit(0)

errors = 0
for f in INSTR.glob("*.json"):
    if f.name == "schema.json":
        continue
    try:
        doc = json.loads(f.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"ERROR: {f.name} -> invalid JSON: {e}")
        errors += 1
        continue
    missing = [k for k in ("id","action","params") if k not in doc]
    if missing:
        print(f"ERROR: {f.name} -> missing keys: {missing}")
        errors += 1

if errors:
    print(f"Found {errors} instruction errors.")
    sys.exit(2)
else:
    print("All instructions look good.")
    sys.exit(0)
