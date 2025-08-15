# core/orchestrator.py
from pathlib import Path
import json
import subprocess
from core.validator import validate_instruction_file, ValidationError

ACTION_MAP_PATH = Path(__file__).parent.parent / "tests" / "action_map.json"

def load_all_instructions():
    """Load and validate all JSON instruction files in /instructions."""
    instructions_dir = Path(__file__).parent.parent / "instructions"
    valid_instructions = []

    for file_path in instructions_dir.glob("*.json"):
        # Skip the schema definition itself
        if file_path.name == "schema.json":
            continue

        try:
            instruction = validate_instruction_file(file_path)
            print(f"✅ Loaded {file_path.name}: {instruction}")
            valid_instructions.append(instruction)
        except ValidationError as e:
            print(f"❌ {file_path.name} failed validation: {e}")

    return valid_instructions  # ✅ inside a function

def run_mapped_tests(valid_instructions):
    """Run only tests mapped to the actions in valid_instructions."""
    if not ACTION_MAP_PATH.exists():
        print(f"⚠ No action_map.json found at {ACTION_MAP_PATH}, running full suite.")
        return subprocess.call(["pytest"])

    with open(ACTION_MAP_PATH, "r", encoding="utf-8") as f:
        action_map = json.load(f)

    tests_to_run = set()
    for instr in valid_instructions:
        action = instr.get("action")
        if action in action_map:
            tests_to_run.update(action_map[action])
        else:
            print(f"⚠ No mapping for action '{action}', running full test suite.")
            return subprocess.call(["pytest"])  # fallback: run everything

    if tests_to_run:
        print(f"🎯 Running mapped tests: {tests_to_run}")
        return subprocess.call(["pytest", *tests_to_run])

    print("⚠ No tests mapped, running full suite.")
    return subprocess.call(["pytest"])

if __name__ == "__main__":
    valid_instrs = load_all_instructions()
    if valid_instrs:
        run_mapped_tests(valid_instrs)

print(f"Validating {file_path}")
instruction = validate_instruction_file(file_path)

