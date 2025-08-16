from pathlib import Path
import json
import subprocess
from core.agent_registry import select_agent_for_step
from core.sandbox_runner import run_in_sandbox

ACTION_MAP_PATH = Path("tests/action_map.json")

def get_tests_for_actions(actions: list[str]) -> list[str]:
    with open(ACTION_MAP_PATH, "r", encoding="utf-8") as f:
        action_map = json.load(f)
    test_files = []
    for action in actions:
        test_files.extend(action_map.get(action, []))
    return sorted(set(test_files))

def run_instruction(instruction: dict) -> dict:
    if instruction.get("sandbox"):
        return run_in_sandbox(instruction)
    else:
        return run_normally(instruction)

def run_normally(instruction: dict) -> dict:
    print(f"[normal] Executing: {instruction['action']}")
    return {
        "status": "normal",
        "output": None
    }

# After parsing instructions
# actions = [step["action"] for step in all_valid_steps]
# test_files = get_tests_for_actions(actions)
# if test_files:
#     subprocess.run(["pytest", *test_files])
# else:
#     subprocess.run(["pytest"])

def normalize_step_capabilities(step: dict) -> None:
    """Normalize step capabilities by ensuring _capabilities key exists."""
    step["_capabilities"] = step.get("capabilities", [])

def run_mapped_tests(all_valid_steps: list[dict]) -> None:
    """Run only mapped tests based on step actions."""
    # Normalize capabilities and assign agents for all steps
    for step in all_valid_steps:
        normalize_step_capabilities(step)
        
        # Agent selection based on capabilities
        capabilities = step.get("capabilities", [])
        step["_agent"] = select_agent_for_step(capabilities)
    
    # Extract actions from all valid steps
    actions = [step["action"] for step in all_valid_steps]
    
    # Get mapped test files
    test_files = get_tests_for_actions(actions)
    
    # Run mapped tests only
    if test_files:
        print(f"🔍 Running mapped tests: {test_files}")
        subprocess.run(["pytest", *test_files])
    else:
        print("⚠️ No mapped tests found - running full suite")
        subprocess.run(["pytest"])