# core/executor.py
import os
import time
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from .actions_api import call_action, create_context
# Import the reporter's line builder to be used by the logger
import core.reporting as reporting

# --- New Logging Functionality ---

LOG_DIR = "orchestrator_artifacts"

def _write_log(steps: list):
    """Write PR-style preview lines to a timestamped log file."""
    os.makedirs(LOG_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = os.path.join(LOG_DIR, f"run-{ts}.log")
    
    # Use the existing reporter to build the lines
    preview_lines = reporting.build_preview_lines(steps)
    
    with open(log_path, "w", encoding="utf-8") as f:
        for line in preview_lines:
            f.write(line + "\n")
            
    return log_path

def run_all(steps: list) -> list:
    """Run a list of steps, enrich them with results, and write a summary log."""
    executed_steps = []
    shared_context = {} # A context that can persist across steps if needed
    
    for i, step in enumerate(steps):
        # The executor's job is to run one step at a time.
        # We reuse the logic from the previous run_agent_task function.
        executed_step = run_step(step, shared_context, i)
        executed_steps.append(executed_step)
        
        # Update shared context for the next step
        if executed_step.get("status") == "ok":
            shared_context.update(executed_step.get("data", {}))

    log_path = _write_log(executed_steps)
    print(f"📄 Log written to {log_path}")
    
    return executed_steps

# --- Core Step Execution Logic (adapted from run_agent_task) ---

def run_step(step: dict, shared_context: dict, step_index: int) -> dict:
    """
    Executes a single step, captures timing and provider metrics,
    and returns the enriched step dictionary.
    """
    # Use the step dict itself as the result container
    step["start_time"] = time.time()
    step.setdefault("metrics", {})
    
    try:
        action_name = step.get("action")
        params = step.get("params", {})
        action_context = create_context(**shared_context, **params)
        
        result = call_action(action_name, action_context)
        
        # Capture provider stats if present
        data_payload = result.get("data", result)
        if isinstance(data_payload, dict):
            if "token_usage" in data_payload:
                step["metrics"]["tokens"] = data_payload["token_usage"]
            # ... add other metrics here ...

        step["status"] = result.get("status", "ok")
        step["message"] = result.get("message", "Completed successfully")
        step.update(result)

    except Exception as e:
        step["status"] = "error"
        step["message"] = str(e)
        logging.error(f"Error executing step '{step.get('id')}': {e}", exc_info=True)

    finally:
        step["end_time"] = time.time()
        step["duration_sec"] = round(step["end_time"] - step["start_time"], 2)

    return step