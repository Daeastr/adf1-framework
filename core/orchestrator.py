# core/orchestrator.py

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

from core.validator import validate_instruction_file, ValidationError

# --- Configurable paths (module‑level so tests can monkeypatch) ---
REPO_ROOT = Path(__file__).resolve().parent.parent
INSTRUCTIONS_DIR = REPO_ROOT / "instructions"
ACTION_MAP_PATH = REPO_ROOT / "tests" / "action_map.json"


def load_all_instructions(raise_on_invalid: bool = True) -> List[Dict[str, Any]]:
    """
    Load and validate all instruction JSON files in INSTRUCTIONS_DIR.

    Skips schema.json.
    If raise_on_invalid=True, re‑raises on first ValidationError.
    If False, logs failures but continues collecting valids.
    """
    valid_instructions: List[Dict[str, Any]] = []

    if not INSTRUCTIONS_DIR.exists():
        print(f"⚠ instructions directory not found at {INSTRUCTIONS_DIR}")
        return valid_instructions
for file_path in instructions_dir.glob("*.json"):
    # ⬇ Skip the schema definition itself
    if file_path.name == "schema.json":
        continue

    try:
        instruction = validate_instruction_file(file_path)
        print(f"✅ Loaded {file_path.name}: {instruction}")
        valid_instructions.append(instruction)
    except ValidationError as e:
        print(f"❌ {file_path.name} failed validation: {e}")

    for file_path in INSTRUCTIONS_DIR.glob("*.json"):
        # Skip the schema definition itself
        if file_path.name == "schema.json":
            continue

        print(f"DEBUG: validating {file_path}")
        try:
            instruction = validate_instruction_file(file_path)
            print(f"✅ Loaded {file_path.name}: {instruction}")
            valid_instructions.append(instruction)
        except ValidationError as e:
            print(f"❌ {file_path.name} failed validation: {e}")
            if raise_on_invalid:
                raise

    return valid_instructions


def _run_full_suite() -> int:
    print("🎯 No reliable mapping available. Running full test suite.")
    return subprocess.call(["pytest"])


def run_mapped_tests(valid_instructions: List[Dict[str, Any]]) -> int:
    """
    Run tests selectively based on action → tests mapping in ACTION_MAP_PATH.
    Fallbacks:
      - If map is missing/unreadable → run full suite.
      - If any action is unmapped → run full suite.
      - If mapped files missing on disk → warn, filter; run full suite if none remain.
    """
    try:
        with open(ACTION_MAP_PATH, "r", encoding="utf-8") as f:
            action_map: Dict[str, List[str]] = json.load(f)
    except FileNotFoundError:
        print(f"⚠ Action map not found at {ACTION_MAP_PATH}")
        return _run_full_suite()
    except json.JSONDecodeError as e:
        print(f"⚠ Action map is not valid JSON: {e}")
        return _run_full_suite()

    tests_to_run: set[str] = set()

    for instr in valid_instructions:
        action = instr.get("action")
        if not isinstance(action, str):
            print(f"⚠ Instruction missing string 'action': {instr}")
            return _run_full_suite()

        mapped = action_map.get(action)
        if not mapped:
            print(f"⚠ No mapping for action '{action}'.")
            return _run_full_suite()

        tests_to_run.update(mapped)

    # Filter out non‑existent test paths
    existing_tests = {t for t in tests_to_run if (REPO_ROOT / t).exists()}
    missing_tests = tests_to_run - existing_tests
    if missing_tests:
        print(f"⚠ Mapped test files not found, skipping: {sorted(missing_tests)}")

    if not existing_tests:
        print("⚠ No existing mapped tests remain after filtering.")
        return _run_full_suite()

    print(f"🎯 Running mapped tests: {sorted(existing_tests)}")
    return subprocess.call(["pytest", *sorted(existing_tests)])


def main() -> int:
    # CLI default is lenient; tests can call with strict=True
    try:
        valid_instrs = load_all_instructions(raise_on_invalid=False)
    except ValidationError:
        return 1

    if not valid_instrs:
        print("ℹ No valid instructions found. Nothing to test.")
        return 0

    return run_mapped_tests(valid_instrs)


if __name__ == "__main__":
    # Ensure repo root is on sys.path so `python -m core.orchestrator` works
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    sys.exit(main())
