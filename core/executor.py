# core/executor.py
import os
import time
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
# Import the real provider that will be called
from .providers.gemini import GeminiProvider
# Import the reporter's line builder to be used by the logger
import core.reporting as reporting

# --- Provider Instantiation ---
gemini_provider = None
if os.getenv("GOOGLE_API_KEY"):
    gemini_provider = GeminiProvider(api_key=os.getenv("GOOGLE_API_KEY"))
else:
    print("Warning: GOOGLE_API_KEY not set. GeminiProvider will not be available.")

# --- New Logging and Batch Execution ---
LOG_DIR = "orchestrator_artifacts"

def _write_log(steps):
    """Write PR-style preview lines to a timestamped log file."""
    os.makedirs(LOG_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = os.path.join(LOG_DIR, f"run-{ts}.log")
    
    # Use the existing reporter to build the lines
    with open(log_path, "w", encoding="utf-8") as f:
        for line in reporting.build_preview_lines(steps):
            f.write(line + "\n")
            
    return log_path

def run_all(steps):
    """Run a list of steps and write a log."""
    executed_steps = []
    shared_context = {} # A context that can persist across steps if needed
    
    for i, step in enumerate(steps):
        # We now pass a shared_context and index to run_step
        executed_step = run_step(step, shared_context, i)
        executed_steps.append(executed_step)

    log_path = _write_log(executed_steps)
    print(f"📄 Log written to {log_path}")
    
    return executed_steps

# --- Core Step Execution Logic ---
def run_step(step: dict, shared_context: dict, step_index: int) -> dict:
    """
    Executes a single step, routing to the live Gemini provider for
    specific actions, and captures all telemetry.
    """
    step["start_time"] = time.time()
    step.setdefault("metrics", {})
    
    try:
        action_name = step.get("action", step.get("name"))

        if action_name == "translate_text" and gemini_provider:
            # ... (live provider routing logic as before)
            params = step.get("params", {})
            result = gemini_provider.translate_text(
                text=params.get("text"), 
                target_lang=params.get("target_lang")
            )
            step["message"] = getattr(result, "message", "")
        else:
            # Fallback for other actions
            result = {"message": f"Action '{action_name}' executed via stub."} 
        
        # Capture metrics
        if hasattr(result, "token_usage"):
            step["metrics"]["tokens"] = result.token_usage
        if hasattr(result, "latency"):
            step["metrics"]["latency"] = result.latency
        if hasattr(result, "cost_usd"):
            step["metrics"]["cost_usd"] = result.cost_usd
        step["status"] = "✅"

    except Exception as e:
        step["status"] = "❌"
        step["message"] = str(e)

    finally:
        step["end_time"] = time.time()
        step["duration_sec"] = round(step["end_time"] - step["start_time"], 2)

    return step
