import uuid
import time
import json
import logging
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
    Executes a single task, captures timing and provider metrics, and logs
    its full output to an artifact file.
    """
    result = {}
    
    # --- Timing and Metrics Hooks ---
    start_time = time.time()
    result["start_time"] = start_time
    result["metrics"] = {}  # NEW: Initialize a container for provider telemetry
    
    try:
        # --- Existing execution logic ---
        action_name = task.get("action")
        params = task.get("params", {})
        action_context = create_context(**shared_context, **params)
        
        action_result = call_action(action_name, action_context)
        result.update(action_result)
        
        # --- NEW: Capture provider metrics from the result ---
        # The action's return value ('action_result') might be a simple dict
        # or a data object. We safely check for common telemetry attributes.
        data_payload = action_result.get("data", action_result) # Check top level or nested data
        
        if isinstance(data_payload, dict):
            # Check for common telemetry keys in the dictionary
            if "token_usage" in data_payload:
                result["metrics"]["tokens"] = data_payload["token_usage"]
            if "latency_ms" in data_payload:
                result["metrics"]["latency_ms"] = data_payload["latency_ms"]
            if "cost_usd" in data_payload:
                result["metrics"]["cost_usd"] = data_payload["cost_usd"]

        if "status" not in result:
            result["status"] = "ok"

    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
        logging.error(f"Error executing action '{task.get('action')}': {e}", exc_info=True)

    finally:
        end_time = time.time()
        result["end_time"] = end_time
        result["duration_sec"] = round(end_time - start_time, 2)
    # --- END Hooks ---

    # --- Existing artifact logging ---
    # We convert the result to JSON for logging after all metrics are added.
    full_output = json.dumps(result, indent=2)
    result["full_output"] = full_output
    task_id = task.get("id", uuid.uuid4().hex)
    step_idx = task.get("_step_index", 1)
    log_path = _save_step_log(task_id, step_idx, full_output)
    result["log_file"] = str(log_path)
    result['artifactPath'] = str(log_path)

    return result