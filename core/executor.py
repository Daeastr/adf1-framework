import uuid
import time
import json
from pathlib import Path
from .actions_api import call_action, create_context

# --- Artifact and Logging Setup ---

ARTIFACTS_DIR = Path("orchestrator_artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

def _save_step_log(task_id: str, step_idx: int, content: str) -> Path:
    """Save full log to artifacts folder and return the Path object."""
    filename = f"{task_id}_step{step_idx}.log"
    path = ARTIFACTS_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path

# --- Core Task Execution Logic ---

def run_agent_task(task: dict, shared_context: dict) -> dict:
    """
    Executes a single task (a step in a plan), captures its start and end
    times, records its duration, and saves its full output to a log file.
    """
    result = {}
    
    # --- TIMESTAMP HOOKS ---
    start_time = time.time()
    result["start_time"] = start_time
    
    try:
        # --- Existing execution logic ---
        action_name = task.get("action")
        params = task.get("params", {})
        action_context = create_context(**shared_context, **params)
        
        # The result of the action is the core payload
        action_result = call_action(action_name, action_context)
        result.update(action_result) # Merge the action's output into our result
        
        # If the action doesn't define a status, assume 'ok'
        if "status" not in result:
            result["status"] = "ok"

    except Exception as e:
        # Capture any exceptions that occur during the action
        result["status"] = "error"
        result["message"] = str(e)
        logging.error(f"Error executing action '{task.get('action')}': {e}", exc_info=True)

    finally:
        # This block is guaranteed to run, even if the action fails
        end_time = time.time()
        result["end_time"] = end_time
        # Calculate and store the duration directly
        result["duration_sec"] = round(end_time - start_time, 2)
    # --- END TIMESTAMP HOOKS ---

    # --- Existing artifact logging ---
    full_output = json.dumps(result, indent=2)
    result["full_output"] = full_output
    task_id = task.get("id", uuid.uuid4().hex)
    step_idx = task.get("_step_index", 1)
    log_path = _save_step_log(task_id, step_idx, full_output)
    result["log_file"] = str(log_path)
    result['artifactPath'] = str(log_path)

    return result