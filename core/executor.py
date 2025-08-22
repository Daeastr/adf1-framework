# core/executor.py
import uuid
import time
import json
from pathlib import Path
from .orchestrator import call_action, create_context # Using the project's actual dispatch logic

# --- Artifact and Logging Setup ---

ARTIFACTS_DIR = Path("orchestrator_artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

def _save_step_log(task_id: str, step_idx: int, content: str) -> str:
    """Save full log to artifacts folder and return file path."""
    filename = f"{task_id}_step{step_idx}.log"
    path = ARTIFACTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(path)

# --- Core Task Execution Logic ---

def run_agent_task(task: dict, shared_context: dict) -> dict:
    """
    Executes a single task, records metadata, and logs its output to an artifact file.
    """
    start = time.time()

    # Dispatch the action (stub or real handler)
    # This replaces the placeholder `_dispatch_somehow(task)` with the actual call
    action_name = task.get("action")
    params = task.get("params", {})
    action_context = create_context(**shared_context, **params)
    result = call_action(action_name, action_context)

    end = time.time()

    # Enrich the result with execution metadata
    result["duration_sec"] = round(end - start, 2)

    # Use the full, serialized result as the log content for completeness
    full_output = json.dumps(result, indent=2)
    result["full_output"] = full_output

    # Save log for artifact upload
    task_id = task.get("id", uuid.uuid4().hex)
    step_idx = task.get("_step_index", 1) # Default to 1 if not provided by orchestrator
    log_path = _save_step_log(task_id, step_idx, full_output)
    result["log_file"] = log_path

    return result