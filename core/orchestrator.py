# core/orchestrator.py
from pathlib import Path
from core.validator import validate_instruction_file, ValidationError

def normalize_step_metadata(step: dict) -> None:
    """
    Normalize step metadata by ensuring _priority and _risk keys exist.
    
    Args:
        step: Step dictionary to normalize (modified in place)
    """
    priority = step.get("priority", "medium")
    risk = step.get("risk", "review")
    step["_priority"] = priority
    step["_risk"] = risk

def load_all_instructions():
    """Load and validate all instruction files, normalizing step metadata."""
    # Define the path to your instructions folder
    instructions_dir = Path(__file__).parent.parent / "instructions"

    for file_path in instructions_dir.glob("*.json"):
        # Skip schema.json itself
        if file_path.name == "schema.json":
            continue
            
        try:
            instruction = validate_instruction_file(file_path)
            
            # Normalize metadata for all steps in the instruction
            if "steps" in instruction:
                for step in instruction["steps"]:
                    normalize_step_metadata(step)
            
            print(f"✅ Loaded {file_path.name}: {instruction}")
            
        except ValidationError as e:
            print(f"❌ {file_path.name} failed validation: {e}")

if __name__ == "__main__":
    load_all_instructions()
priority = step.get("priority", "medium")
risk = step.get("risk", "review")
step["_priority"] = priority
step["_risk"] = risk



