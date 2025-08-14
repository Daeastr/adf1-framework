# core/parser.py

import sys
from pathlib import Path
import json
import jsonschema

from core.schema_loader import load_schema
from core.validator import validate_instruction
from core.config import INSTRUCTIONS_DIR


def main():
    schema = load_schema()

    # If user passed file paths, use them; else scan the instructions folder
    args = sys.argv[1:]
    target_files = [Path(p) for p in args] if args else INSTRUCTIONS_DIR.glob("*.json")

    found_any = False
    for file_path in target_files:
        if file_path.exists() and file_path.suffix.lower() == ".json":
            found_any = True
            try:
                validate_instruction(file_path, schema)
                print(f"[OK] {file_path.name} is valid.")
            except jsonschema.exceptions.ValidationError as e:
                print(f"[ERROR] {file_path.name} — {e.message}")
            except json.JSONDecodeError as e:
                print(f"[ERROR] {file_path.name} — Invalid JSON: {e}")
        else:
            if args:  # Only complain about missing files if explicitly asked for
                print(f"[ERROR] {file_path} not found or not a JSON file.")

    if not found_any and not args:
        print(f"[ERROR] No JSON files found in {INSTRUCTIONS_DIR}")


if __name__ == "__main__":
    main()

