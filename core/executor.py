import sys
import json
import os
import shutil
import uuid
import time
from pathlib import Path
from typing import Dict, Any

ARTIFACTS_DIR = Path("orchestrator_artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

def _save_step_log(task_id: str, step_idx: int, content: str) -> str:
    filename = f"{task_id}_step{step_idx}.log"
    path = ARTIFACTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(path)

def apply_patch(patch):
    target_file = patch.get("target")
    new_content = patch.get("content")

    if not target_file or not new_content:
        print("Invalid patch format.")
        return

    # Backup original
    backup_path = f"{target_file}.bak"
    shutil.copyfile(target_file, backup_path)
    print(f"Backup created: {backup_path}")

    # Apply patch
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Patch applied to: {target_file}")

def run_instruction(instruction_path: str):
    with open(instruction_path, "r", encoding="utf-8") as f:
        instruction = json.load(f)
    action = instruction.get("action")
    print(f"Sandboxed execution: {action}")
    if action == "apply_patch":
        apply_patch(instruction.get("patch", {}))

def run_agent_task(task: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    result = _dispatch_somehow(task)  # Your stub/container exec
    end = time.time()

    result["duration_sec"] = round(end - start, 2)
    full_output = result.get("output", "")
    result["full_output"] = full_output

    # Save artifact
    task_id = task.get("id", uuid.uuid4().hex)
    step_idx = task.get("_step_index", 1)
    result["log_file"] = _save_step_log(task_id, step_idx, full_output)

    return result

def _dispatch_somehow(task: Dict[str, Any]) -> Dict[str, Any]:
    """Stub function for task execution - replace with actual implementation"""
    return {
        "status": "completed",
        "output": f"Executed task: {task.get('action', 'unknown')}"
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python execute.py <instruction_file>")
        sys.exit(1)

    try:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            instruction = json.load(f)

        print(f"Executing action: {instruction['action']}")
        print(f"Priority: {instruction['priority']}")
        print(f"Risk: {instruction['risk']}")
        print(f"Capabilities: {instruction['capabilities']}")
        
        if 'sandbox' in instruction:
            sandbox = instruction['sandbox']
            print(f"Sandbox config - Image: {sandbox['image']}")
            if 'cpu' in sandbox:
                print(f"CPU: {sandbox['cpu']}")
            if 'memory' in sandbox:
                print(f"Memory: {sandbox['memory']}")
            if 'network' in sandbox:
                print(f"Network: {sandbox['network']}")

        action = instruction.get("action")
        print(f"Sandboxed execution: {action}")

        if action == "apply_patch":
            apply_patch(instruction.get("patch", {}))
        
        print("✅ Execution completed successfully")
        
    except Exception as e:
        print(f"❌ Error executing instruction: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
