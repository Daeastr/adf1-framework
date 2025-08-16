from pathlib import Path
import json
import subprocess
from core.agent_registry import select_agent_for_step
from core.sandbox_runner import run_in_sandbox
from core.execute import run_agent_task  # import your upgraded executor

ACTION_MAP_PATH = Path("tests/action_map.json")
INSTRUCTIONS_DIR = Path(__file__).parent.parent / "instructions"
INSTR_DIR = Path(__file__).parent.parent / "instructions"

def collect_actions_safe():
    """Yield unique action values from valid single‑object instruction files."""
    actions = set()
    for f in INSTR_DIR.glob("*.json"):
        try:
            with f.open(encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and "id" in data and "action" in data:
                actions.add(data["action"])
        except Exception as e:
            print(f"Skipping invalid JSON in {f.name}")
    return sorted(actions)

def get_tests_for_actions(actions: list[str]) -> list[str]:
    with open(ACTION_MAP_PATH, "r", encoding="utf-8") as f:
        action_map = json.load(f)
    test_files = []
    for action in actions:
        test_files.extend(action_map.get(action, []))
    return sorted(set(test_files))

def load_all_instructions():
    """Enhanced loader/validator for JSON instruction documents"""
    instructions = []
    if not INSTRUCTIONS_DIR.exists():
        print(f"⚠️ Instructions directory not found: {INSTRUCTIONS_DIR}")
        return instructions
    
    for json_file in INSTRUCTIONS_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                instruction = json.load(f)
            
            # Basic validation
            if not instruction.get("action"):
                print(f"⚠️ Skipping {json_file.name}: missing 'action' field")
                continue
            
            # Ensure ID exists
            if not instruction.get("id"):
                instruction["id"] = json_file.stem
            
            instructions.append(instruction)
            print(f"✅ Loaded instruction: {instruction['id']} - {instruction['action']}")
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing {json_file.name}: {e}")
        except Exception as e:
            print(f"❌ Error loading {json_file.name}: {e}")
    
    return instructions

def run_instruction(instruction: dict) -> dict:
    """Legacy instruction runner - maintained for compatibility"""
    if instruction.get("sandbox"):
        return run_in_sandbox(instruction)
    else:
        return run_normally(instruction)

def run_normally(instruction: dict) -> dict:
    """Legacy normal execution - maintained for compatibility"""
    print(f"[normal] Executing: {instruction['action']}")
    return {
        "status": "normal",
        "output": None
    }

def normalize_step_capabilities(step: dict) -> None:
    """Normalize step capabilities by ensuring _capabilities key exists."""
    step["_capabilities"] = step.get("capabilities", [])

def run_all_validated():
    """Enhanced function to run all validated instructions with improved executor"""
    valid_instrs = load_all_instructions()
    
    if not valid_instrs:
        print("❌ No valid instructions found to execute")
        return
    
    print(f"🚀 Running {len(valid_instrs)} validated instructions...")
    
    results = []
    for step_idx, instr in enumerate(valid_instrs, start=1):
        print(f"\n--- Executing Step {step_idx}/{len(valid_instrs)} ---")
        
        # Prepare instruction for enhanced executor
        instr["_step_index"] = step_idx  # so executor can name log files
        
        # Normalize capabilities and assign agent
        normalize_step_capabilities(instr)
        capabilities = instr.get("capabilities", [])
        instr["_agent"] = select_agent_for_step(capabilities)
        
        # Run with enhanced executor
        try:
            result = run_agent_task(instr)
            results.append(result)
            
            print(f"✅ [{instr['id']}] Completed in {result['duration_sec']}s")
            print(f"📄 Log saved at: {result['log_file']}")
            
            if result.get("status") == "failed":
                print(f"⚠️ Task failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ [{instr['id']}] Execution failed: {e}")
            results.append({
                "status": "failed",
                "error": str(e),
                "duration_sec": 0,
                "log_file": None
            })
    
    # Summary report
    print(f"\n=== Execution Summary ===")
    successful = sum(1 for r in results if r.get("status") == "completed")
    failed = len(results) - successful
    total_duration = sum(r.get("duration_sec", 0) for r in results)
    
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏱ Total Duration: {total_duration:.2f}s")
    
    return results

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

def run_tests_and_execute():
    """Combined function to run tests and then execute validated instructions"""
    print("🧪 Phase 1: Loading and testing instructions...")
    valid_instrs = load_all_instructions()
    
    if valid_instrs:
        # Run mapped tests first
        run_mapped_tests(valid_instrs)
        
        print("\n🚀 Phase 2: Executing validated instructions...")
        return run_all_validated()
    else:
        print("❌ No valid instructions to test or execute")
        return []

# Legacy comment preserved for reference:
# After parsing instructions
# actions = [step["action"] for step in all_valid_steps]
# test_files = get_tests_for_actions(actions)
# if test_files:
#     subprocess.run(["pytest", *test_files])
# else:
#     subprocess.run(["pytest"])

if __name__ == "__main__":
    valid_actions = collect_actions_safe()
    if valid_actions:
        run_mapped_tests([{"action": a} for a in valid_actions])