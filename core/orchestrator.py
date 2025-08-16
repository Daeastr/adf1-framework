# core/orchestrator.py
import json
import subprocess
from pathlib import Path
from core.validator import validate_instruction_file, ValidationError

# Define paths
ACTION_MAP_PATH = Path("tests/action_map.json")

def get_tests_for_actions(actions: list[str]) -> list[str]:
    """
    Get test files for given actions from action map.
    
    Args:
        actions: List of action names to get tests for
        
    Returns:
        Sorted list of unique test files
    """
    try:
        with open(ACTION_MAP_PATH, "r", encoding="utf-8") as f:
            action_map = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Action map file not found: {ACTION_MAP_PATH}")
        return []
    except json.JSONDecodeError as e:
        print(f"⚠️ Invalid JSON in action map: {e}")
        return []
    
    test_files = []
    for action in actions:
        test_files.extend(action_map.get(action, []))
    return sorted(set(test_files))

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

def load_all_instructions() -> list[dict]:
    """
    Load and validate all instruction files, normalizing step metadata.
    
    Returns:
        List of validated and normalized instruction dictionaries
    """
    # Define the path to your instructions folder
    instructions_dir = Path(__file__).parent.parent / "instructions"
    loaded_instructions = []

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
            
            loaded_instructions.append(instruction)
            print(f"✅ Loaded {file_path.name}: {instruction.get('id', 'unknown')}")
            
        except ValidationError as e:
            print(f"❌ {file_path.name} failed validation: {e}")
        except Exception as e:
            print(f"❌ Unexpected error loading {file_path.name}: {e}")
    
    return loaded_instructions

def get_all_actions_from_instructions(instructions: list[dict]) -> list[str]:
    """
    Extract all unique actions from loaded instructions.
    
    Args:
        instructions: List of instruction dictionaries
        
    Returns:
        List of unique action names
    """
    actions = []
    for instruction in instructions:
        if "steps" in instruction:
            for step in instruction["steps"]:
                if "action" in step:
                    actions.append(step["action"])
    return sorted(set(actions))

def get_all_valid_steps(instructions: list[dict]) -> list[dict]:
    """
    Extract all valid steps from loaded instructions.
    
    Args:
        instructions: List of instruction dictionaries
        
    Returns:
        List of all step dictionaries from all instructions
    """
    all_valid_steps = []
    for instruction in instructions:
        if "steps" in instruction:
            all_valid_steps.extend(instruction["steps"])
    return all_valid_steps

def run_tests_for_instructions(instructions: list[dict]) -> None:
    """
    Run tests based on actions found in valid instructions.
    
    Args:
        instructions: List of validated instruction dictionaries
    """
    # Get all valid steps after parsing all valid instructions
    all_valid_steps = get_all_valid_steps(instructions)
    
    if not all_valid_steps:
        print("⚠️ No valid steps found - skipping test execution")
        return
    
    # Extract actions from all valid steps
    actions = [step["action"] for step in all_valid_steps if "action" in step]
    
    if not actions:
        print("⚠️ No actions found in valid steps - skipping test execution")
        return
    
    # Get test files for these actions
    test_files = get_tests_for_actions(actions)
    
    if test_files:
        print(f"🔍 Running mapped tests: {test_files}")
        try:
            result = subprocess.run(["pytest", *test_files], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ All mapped tests passed")
            else:
                print(f"❌ Some mapped tests failed (exit code: {result.returncode})")
                if result.stdout:
                    print("STDOUT:", result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
        except FileNotFoundError:
            print("❌ pytest not found - please install pytest")
        except Exception as e:
            print(f"❌ Error running tests: {e}")
    else:
        print("⚠️ No mapped tests found — running full suite")
        try:
            result = subprocess.run(["pytest"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Full test suite passed")
            else:
                print(f"❌ Some tests failed in full suite (exit code: {result.returncode})")
        except FileNotFoundError:
            print("❌ pytest not found - please install pytest")
        except Exception as e:
            print(f"❌ Error running full test suite: {e}")

def main():
    """Main function to demonstrate the orchestrator functionality."""
    print("🔄 Loading all instructions...")
    instructions = load_all_instructions()
    
    if instructions:
        print(f"\n📊 Successfully loaded {len(instructions)} instructions")
        
        # Get all actions from loaded instructions
        actions = get_all_actions_from_instructions(instructions)
        if actions:
            print(f"🎯 Found {len(actions)} unique actions: {actions}")
        
        # Run tests based on the loaded instructions
        run_tests_for_instructions(instructions)
    else:
        print("❌ No instructions were loaded successfully")

if __name__ == "__main__":
    main()