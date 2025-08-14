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
