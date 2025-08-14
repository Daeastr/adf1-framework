# core/orchestrator.py

from pathlib import Path
from core.validator import validate_instruction_file, ValidationError

def load_all_instructions():
    instructions_dir = Path(__file__).parent.parent / "instructions"
    for file_path in instructions_dir.glob("*.json"):
        # ⬇ Skip the schema definition itself
        if file_path.name == "schema.json":
            continue

        try:
            instruction = validate_instruction_file(file_path)
            print(f"✅ Loaded {file_path.name}: {instruction}")
        except ValidationError as e:
            print(f"❌ {file_path.name} failed validation: {e}")

if __name__ == "__main__":
    load_all_instructions()
    import json
import subprocess

ACTION_MAP_PATH = Path(__file__).parent.parent / "tests" / "action_map.json"

def run_mapped_tests(valid_instructions):
    with open(ACTION_MAP_PATH, "r", encoding="utf-8") as f:
        action_map = json.load(f)

    tests_to_run = set()

    for instr in valid_instructions:
        action = instr.get("action")
        if action in action_map:
            tests_to_run.update(action_map[action])
        else:
            print(f"⚠ No mapping for action '{action}', will require full test suite.")
            return subprocess.call(["pytest"])  # fallback: run everything

    if tests_to_run:
        print(f"🎯 Running mapped tests: {tests_to_run}")
        return subprocess.call(["pytest", *tests_to_run])

def load_all_instructions():
    instructions_dir = Path(__file__).parent.parent / "instructions"
    valid_instructions = []
    for file_path in instructions_dir.glob("*.json"):
        if file_path.name == "schema.json":
            continue
        try:
            instruction = validate_instruction_file(file_path)
            print(f"✅ Loaded {file_path.name}: {instruction}")
            valid_instructions.append(instruction)
        except ValidationError as e:
            print(f"❌ {file_path.name} failed validation: {e}")
    return valid_instructions

if __name__ == "__main__":
    valid_instrs = load_all_instructions()
    if valid_instrs:
        run_mapped_tests(valid_instrs)

