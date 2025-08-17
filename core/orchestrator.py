# core/orchestrator.py
import time
from pathlib import Path
import argparse
import json
import subprocess
import re
from itertools import cycle
from core.agent_registry import select_agent_for_step
import core.sandbox_runner as sandbox_runner
from core.executor import run_agent_task
from core.validator import validate_instruction_file, ValidationError

ACTION_MAP_PATH = Path("tests/action_map.json")
INSTRUCTIONS_DIR = Path(__file__).parent.parent / "instructions"
INSTR_DIR = Path(__file__).parent.parent / "instructions"

# Files to skip when parsing instructions
SKIP_FILES = {"schema.json"}

# ANSI color codes for step coloring
STEP_COLORS = cycle([
    "\033[36m",  # cyan
    "\033[35m",  # magenta
    "\033[34m",  # blue
    "\033[33m",  # yellow
    "\033[32m",  # green
])
RESET = "\033[0m"

def tail_logs(paths: list[Path]):
    """Enhanced multi-file log tailing with labeled output"""
    last_sizes = {p: 0 for p in paths}
    
    print(f"📋 Following {len(paths)} log file(s):")
    for p in paths:
        print(f"  • {p}")
    print("🔄 Streaming updates... (Ctrl+C to stop)")
    print("-" * 60)

    try:
        while True:
            for p in paths:
                if p.exists():
                    size = p.stat().st_size
                    if size > last_sizes[p]:
                        with open(p, "r", encoding="utf-8") as f:
                            f.seek(last_sizes[p])
                            chunk = f.read()
                            if chunk:
                                prefix = f"[{p.stem}] "
                                for line in chunk.splitlines():
                                    print(prefix + line)
                        last_sizes[p] = size
                elif last_sizes[p] == 0:
                    # Only show "waiting" message once per file
                    print(f"⏳ [{p.stem}] Waiting for log file to be created...")
                    last_sizes[p] = -1  # Mark as "waiting message shown"
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n📋 Log following stopped for {len(paths)} file(s).")

def tail_logs_colored(paths: list[Path], levels: list[str] = None):
    """Enhanced multi-file log tailing with ANSI colors and level filtering"""
    patterns = None
    if levels:
        joined = "|".join([re.escape(lvl.upper()) for lvl in levels])
        patterns = re.compile(rf"\b({joined})\b", re.IGNORECASE)

    step_colors = {p: next(STEP_COLORS) for p in paths}
    last_sizes = {p: 0 for p in paths}
    
    print(f"📋 Following {len(paths)} log file(s) with colors:")
    for p in paths:
        color = step_colors[p]
        print(f"  {color}• {p}{RESET}")
    if levels:
        print(f"🔍 Filtering for levels: {', '.join(levels)}")
    print("🔄 Streaming updates... (Ctrl+C to stop)")
    print("-" * 60)

    try:
        while True:
            for p in paths:
                if p.exists():
                    size = p.stat().st_size
                    if size > last_sizes[p]:
                        with open(p, "r", encoding="utf-8") as f:
                            f.seek(last_sizes[p])
                            for line in f:
                                line = line.strip()
                                if not line:
                                    continue
                                    
                                # Apply level filtering if specified
                                if patterns is None or patterns.search(line):
                                    color = step_colors[p]
                                    
                                    # Override for severity highlighting
                                    line_upper = line.upper()
                                    if "ERROR" in line_upper:
                                        color = "\033[31m"  # red
                                    elif "WARN" in line_upper:
                                        color = "\033[33m"  # yellow
                                    elif "INFO" in line_upper:
                                        color = "\033[37m"  # white/bright
                                    elif "DEBUG" in line_upper:
                                        color = "\033[90m"  # dark gray
                                    
                                    print(f"{color}[{p.stem}] {line}{RESET}")
                        last_sizes[p] = size
                elif last_sizes[p] == 0:
                    # Only show "waiting" message once per file
                    color = step_colors[p]
                    print(f"⏳ {color}[{p.stem}]{RESET} Waiting for log file to be created...")
                    last_sizes[p] = -1  # Mark as "waiting message shown"
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n📋 Log following stopped for {len(paths)} file(s).")

def load_valid_instructions():
    """Load only well-formed instruction docs, skip schema/invalid JSONs."""
    valid = []
    for f in INSTR_DIR.glob("*.json"):
        if f.name.lower() == "schema.json":
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"⚠ Skipping invalid JSON in {f.name}")
            continue
        if all(k in data for k in ("id", "action", "params")):
            valid.append(data)
        else:
            print(f"⚠ Skipping non‑instruction file {f.name}")
    return valid

def gather_actions_from_valid_instructions() -> list[str]:
    """Load only valid instruction files and collect their action fields."""
    actions = []
    for json_file in INSTRUCTIONS_DIR.glob("*.json"):
        try:
            instr = validate_instruction_file(json_file)
        except (ValidationError, json.JSONDecodeError):
            print(f"ℹ️ Skipping non‑instruction or invalid JSON: {json_file.name}")
            continue
        if "action" in instr:
            actions.append(instr["action"])
    return actions

def get_tests_for_actions(actions: list[str]) -> list[str]:
    """Map action names to their test files."""
    try:
        with open(ACTION_MAP_PATH, "r", encoding="utf-8") as f:
            action_map = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️ Could not load action map from {ACTION_MAP_PATH}: {e}")
        return []
    
    test_files = []
    for action in actions:
        test_files.extend(action_map.get(action, []))
    return sorted(set(test_files))

def load_all_instructions():
    """Load + validate all instruction files, skipping non‑instructions."""
    instructions = []
    if not INSTRUCTIONS_DIR.exists():
        print(f"⚠️ Instructions directory not found: {INSTRUCTIONS_DIR}")
        return instructions

    for json_file in INSTRUCTIONS_DIR.glob("*.json"):
        if json_file.name in SKIP_FILES:
            print(f"ℹ️ Skipping helper file: {json_file.name}")
            continue

        try:
            instr = validate_instruction_file(json_file)
        except (ValidationError, json.JSONDecodeError) as e:
            print(f"⚠️ Skipping invalid JSON in {json_file.name}: {e}")
            continue

        instructions.append(instr)
        print(f"✅ Loaded {instr['id']} — {instr['action']}")

    return instructions

def run_instruction(instruction: dict) -> dict:
    """Legacy instruction runner - maintained for compatibility"""
    if instruction.get("sandbox"):
        return sandbox_runner.run_in_sandbox(instruction)
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

def create_execution_summary(executed_steps: list[dict]) -> dict:
    """Create a comprehensive execution summary with log file information."""
    successful = sum(1 for step in executed_steps if step.get("status") == "completed")
    failed = len(executed_steps) - successful
    total_duration = sum(step.get("duration_sec", 0) for step in executed_steps)
    
    return {
        "summary": {
            "total_steps": len(executed_steps),
            "successful": successful,
            "failed": failed,
            "total_duration_sec": total_duration
        },
        "steps": executed_steps
    }

def run_all_validated():
    """Enhanced function to run all validated instructions with improved executor"""
    valid_instrs = load_all_instructions()
    
    if not valid_instrs:
        print("❌ No valid instructions found to execute")
        return []
    
    print(f"🚀 Running {len(valid_instrs)} validated instructions...")
    
    executed_steps = []
    for step_idx, instr in enumerate(valid_instrs, start=1):
        print(f"\n--- Executing Step {step_idx}/{len(valid_instrs)} ---")
        
        instr["_step_index"] = step_idx
        normalize_step_capabilities(instr)
        capabilities = instr.get("capabilities", [])
        instr["_agent"] = select_agent_for_step(capabilities)
        
        step_record = {
            "id": instr["id"],
            "action": instr["action"],
            "step_index": step_idx,
            "agent": instr["_agent"],
            "capabilities": capabilities
        }
        
        try:
            result = run_agent_task(instr)
            
            step_record.update({
                "status": result.get("status", "unknown"),
                "duration_sec": result.get("duration_sec", 0),
                "log_file": result.get("log_file"),
                "output": result.get("output"),
                "error": result.get("error")
            })
            
            executed_steps.append(step_record)
            
            print(f"✅ [{instr['id']}] Completed in {result['duration_sec']}s")
            if result.get("log_file"):
                print(f"📄 Log saved at: {result['log_file']}")
            
            if result.get("status") == "failed":
                print(f"⚠️ Task failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ [{instr['id']}] Execution failed: {e}")
            step_record.update({
                "status": "failed",
                "error": str(e),
                "duration_sec": 0,
                "log_file": None
            })
            executed_steps.append(step_record)
    
    print(f"\n=== Execution Summary ===")
    successful = sum(1 for step in executed_steps if step.get("status") == "completed")
    failed = len(executed_steps) - successful
    total_duration = sum(step.get("duration_sec", 0) for step in executed_steps)
    
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏱ Total Duration: {total_duration:.2f}s")
    
    return executed_steps

def run_mapped_tests(all_valid_steps: list[dict]) -> None:
    """Run only mapped tests based on step actions."""
    for step in all_valid_steps:
        normalize_step_capabilities(step)
        capabilities = step.get("capabilities", [])
        step["_agent"] = select_agent_for_step(capabilities)
    
    actions = [step["action"] for step in all_valid_steps]
    test_files = get_tests_for_actions(actions)
    
    if test_files:
        print(f"🔍 Running mapped tests: {test_files}")
        subprocess.run(["pytest", *test_files])
    else:
        print("⚠️ No mapped tests found - running full suite")
        subprocess.run(["pytest"])

def run_tests_and_execute():
    """Combined function to run tests and then execute validated instructions"""
    print("🧪 Phase 1: Loading and testing instructions...")
    mapping_instrs = load_valid_instructions()
    all_instrs = load_all_instructions()

    if not all_instrs:
        print("❌ No valid instructions to execute")
        return []

    if mapping_instrs:
        run_mapped_tests(mapping_instrs)
    else:
        print("⚠️ No strictly valid mapping instructions found - running full test suite")
        subprocess.run(["pytest"])

    print("\n🚀 Phase 2: Executing validated instructions...")
    return run_all_validated()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AADF Orchestrator - Execute or parse instruction files")
    parser.add_argument("--parse-only", action="store_true", 
                       help="Only parse and output instructions as JSON, don't execute")
    parser.add_argument("--step-id", type=str,
                       help="Execute only the step with the specified ID")
    parser.add_argument("--output-execution-json", action="store_true",
                       help="Output execution results as JSON for Plan Preview")
    # Updated --follow-log to support multiple files
    parser.add_argument("--follow-log", nargs="+", 
                       help="One or more log files to tail with labeled output")
    # New --levels flag for filtering
    parser.add_argument("--levels", nargs="+",
                       help="Filter log output to only show specified levels (ERROR, WARN, INFO, DEBUG)")
    parser.add_argument("instruction_file", nargs="?", 
                       help="Specific instruction file to execute (optional)")
    
    args = parser.parse_args()
    
    # Handle enhanced --follow-log mode for multiple files
    if args.follow_log:
        log_paths = [Path(p) for p in args.follow_log]
        
        # Use colored tailing if levels are specified, otherwise use regular tailing
        if args.levels:
            tail_logs_colored(log_paths, args.levels)
        else:
            tail_logs(log_paths)
        exit(0)
    
    # Load instructions
    all_instrs = load_all_instructions()
    
    if not all_instrs:
        print("No valid instructions found.")
        raise SystemExit(0)
    
    # Parse-only mode
    if args.parse_only:
        print(json.dumps(all_instrs, indent=None, separators=(',', ':')))
        exit(0)
    
    # Single step execution
    if args.step_id:
        target_step = next((step for step in all_instrs if step['id'] == args.step_id), None)
        if not target_step:
            print(f"❌ Step with ID '{args.step_id}' not found")
            raise SystemExit(1)
        
        print(f"🎯 Executing single step: {args.step_id}")
        
        target_step["_step_index"] = 1
        normalize_step_capabilities(target_step)
        capabilities = target_step.get("capabilities", [])
        target_step["_agent"] = select_agent_for_step(capabilities)
        
        try:
            result = run_agent_task(target_step)
            
            step_record = {
                "id": target_step["id"],
                "action": target_step["action"],
                "step_index": 1,
                "agent": target_step["_agent"],
                "capabilities": capabilities,
                "status": result.get("status", "unknown"),
                "duration_sec": result.get("duration_sec", 0),
                "log_file": result.get("log_file"),
                "output": result.get("output"),
                "error": result.get("error")
            }
            
            print(f"✅ [{target_step['id']}] Completed in {result['duration_sec']}s")
            if result.get("log_file"):
                print(f"📄 Log saved at: {result['log_file']}")
            
            if result.get("status") == "failed":
                print(f"⚠️ Task failed: {result.get('error', 'Unknown error')}")
                raise SystemExit(1)
            else:
                print(f"🎉 Step '{args.step_id}' executed successfully!")
                
                if args.output_execution_json:
                    execution_summary = create_execution_summary([step_record])
                    print("\n" + json.dumps(execution_summary, indent=2))
                
                raise SystemExit(0)
                
        except Exception as e:
            print(f"❌ [{target_step['id']}] Execution failed: {e}")
            raise SystemExit(1)
    
    # Single instruction file execution
    if args.instruction_file:
        print(f"🎯 Executing specific instruction file: {args.instruction_file}")
        # Implementation for single file execution would go here
    
    # Normal execution path
    mapping_instrs = load_valid_instructions()
    actions = [step["action"] for step in (mapping_instrs or []) if "action" in step]
    test_files = get_tests_for_actions(actions)

    if test_files:
        print(f"🎯 Running mapped tests: {test_files}")
        subprocess.run(["pytest", *test_files], check=False)
    else:
        print("⚠️ No mapped tests found — running full suite")
        subprocess.run(["pytest"], check=False)
    
    print("\n🚀 Phase 2: Executing all validated instructions...")
    executed_steps = run_all_validated()
    
    if args.output_execution_json:
        execution_summary = create_execution_summary(executed_steps)
        print("\n=== EXECUTION JSON FOR PLAN PREVIEW ===")
        print(json.dumps(execution_summary, indent=2))