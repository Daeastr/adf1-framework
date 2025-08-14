from pathlib import Path
from core.validator import validate_instruction_file, ValidationError

def load_instruction(path_str: str):
    """Load and validate an instruction JSON file."""
    path = Path(path_str)
    try:
        instruction = validate_instruction_file(path)
    except ValidationError as e:
        print(f"❌ Validation failed: {e}")
        return None
    # Placeholder for future sequencing/execution logic
    print(f"✅ Instruction loaded: {instruction}")
    return instruction

if __name__ == "__main__":
    # Demo run
    load_instruction("instructions/demo.json")
