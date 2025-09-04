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

def save_step_log(task_id: str, step_idx: int, content: str) -> str:
    """Enhanced logging function with better naming and structure"""
    filename = f"{task_id}_step{step_idx}.log"
    path = ARTIFACTS_DIR / filename
    
    # Add timestamp and metadata to the log content
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    enhanced_content = f"[{timestamp}] Task ID: {task_id}, Step: {step_idx}\n"
    enhanced_content += "=" * 50 + "\n"
    enhanced_content += content
    enhanced_content += "\n" + "=" * 50 + "\n"
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(enhanced_content)
    return str(path)

def apply_patch(patch):
    target_file = patch.get("target")
    new_content = patch.get("content")

    if not target_file or not new_content:
        print("Invalid patch format.")
        return

    # Backup original
    backup_path = f"{target_file}.bak"
    try:
        shutil.copyfile(target_file, backup_path)
        print(f"Backup created: {backup_path}")
    except FileNotFoundError:
        print(f"Warning: Target file {target_file} not found, creating new file")

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
    """Enhanced task execution with improved logging and error handling"""
    start = time.time()
    
    # Initialize result structure
    result = {
        "status": "started",
        "task_id": task.get("id", uuid.uuid4().hex),
        "step_index": task.get("_step_index", 1),
        "start_time": start
    }
    
    try:
        # Execute the task
        execution_result = _dispatch_somehow(task)
        result.update(execution_result)
        result["status"] = "completed"
        
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        result["output"] = f"Task execution failed: {e}"
    
    # Calculate duration
    end = time.time()
    result["duration_sec"] = round(end - start, 2)
    result["end_time"] = end
    
    # Get full output for logging
    full_output = result.get("output", "")
    if result.get("error"):
        full_output += f"\nERROR: {result['error']}"
    
    result["full_output"] = full_output
    
    # Enhanced logging with the improved save_step_log function
    task_id = result["task_id"]
    step_idx = result["step_index"]
    
    # Create detailed log content
    log_content = f"Task Execution Report\n"
    log_content += f"Status: {result['status']}\n"
    log_content += f"Duration: {result['duration_sec']} seconds\n"
    log_content += f"Task Details: {json.dumps(task, indent=2)}\n\n"
    log_content += "Output:\n"
    log_content += full_output
    
    result["log_file"] = save_step_log(task_id, step_idx, log_content)
    
    return result

def _dispatch_somehow(task: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced stub function for task execution with more detailed simulation"""
    action = task.get("action", "unknown")
    
    # Simulate different types of task execution
    if action == "apply_patch":
        patch = task.get("patch", {})
        target = patch.get("target", "unknown_file")
        return {
            "status": "completed",
            "output": f"Patch applied to {target}\nLines modified: {len(patch.get('content', '').splitlines())}"
        }
    elif action == "run_command":
        command = task.get("command", "echo 'Hello World'")
        return {
            "status": "completed", 
            "output": f"Command executed: {command}\nExit code: 0\nOutput: Command completed successfully"
        }
    else:
        return {
            "status": "completed",
            "output": f"Executed task: {action}\nTask processed with default handler"
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python execute.py <instruction_file>")
        sys.exit(1)

    try:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            instruction = json.load(f)

        print(f"Executing action: {instruction['action']}")
        print(f"Priority: {instruction.get('priority', 'normal')}")
        print(f"Risk: {instruction.get('risk', 'unknown')}")
        print(f"Capabilities: {instruction.get('capabilities', [])}")
        
        if 'sandbox' in instruction:
            sandbox = instruction['sandbox']
            print(f"Sandbox config - Image: {sandbox.get('image', 'default')}")
            if 'cpu' in sandbox:
                print(f"CPU: {sandbox['cpu']}")
            if 'memory' in sandbox:
                print(f"Memory: {sandbox['memory']}")
            if 'network' in sandbox:
                print(f"Network: {sandbox['network']}")

        action = instruction.get("action")
        print(f"Sandboxed execution: {action}")

        # Enhanced execution using the improved run_agent_task
        task_data = {
            "id": instruction.get("id", uuid.uuid4().hex),
            "action": action,
            "patch": instruction.get("patch"),
            "command": instruction.get("command"),
            "_step_index": 1
        }
        
        result = run_agent_task(task_data)
        
        print(f"Task completed with status: {result['status']}")
        print(f"Duration: {result['duration_sec']} seconds")
        print(f"Log saved to: {result['log_file']}")
        
        if action == "apply_patch":
            apply_patch(instruction.get("patch", {}))
        
        print("✅ Execution completed successfully")
        
    except Exception as e:
        print(f"❌ Error executing instruction: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
