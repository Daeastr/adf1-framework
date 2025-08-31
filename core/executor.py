# core/executor.py
import os
import time
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
# Note: The import from actions_api is removed for this self-contained test.
# from .actions_api import call_action, create_context
import core.reporting as reporting

# --- Inlined Stubs for Isolated Testing ---

class DummyResult:
    """A fake result object to test the executor's metrics capture."""
    def __init__(self, message="OK", tokens=512, latency=0.42, cost=0.0021):
        self.message = message
        self.token_usage = tokens
        self.latency = latency
        self.cost_usd = cost

def _execute_action(step: dict, shared_context: dict) -> DummyResult:
    """
    A private, inlined stub that mimics a real action call and returns a
    DummyResult with telemetry.
    """
    step_name = step.get('name', step.get('action', 'unknown_step'))
    print(f"Executing dummy action for: {step_name}")
    return DummyResult(message=f"Stubbed {step_name}")


# --- Logging and Execution Logic ---

LOG_DIR = "orchestrator_artifacts"

def _write_log(steps: list):
    """Write PR-style preview lines to a timestamped log file."""
    os.makedirs(LOG_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = os.path.join(LOG_DIR, f"run-{ts}.log")
    
    preview_lines = reporting.build_preview_lines(steps)
    
    with open(log_path, "w", encoding="utf-8") as f:
        for line in preview_lines:
            f.write(line + "\n")
            
    return log_path

def run_all(steps: list) -> list:
    """Run a list of steps, enrich them with results, and write a summary log."""
    executed_steps = []
    shared_context = {}
    
    for i, step in enumerate(steps):
        executed_step = run_step(step, shared_context, i)
        executed_steps.append(executed_step)
        
        # In a real scenario, you might update shared_context here.

    log_path = _write_log(executed_steps)
    print(f"📄 Log written to {log_path}")
    
    return executed_steps

def run_step(step: dict, shared_context: dict, step_index: int) -> dict:
    """
    Executes a single step using the internal stub, captures all telemetry,
    and returns the enriched step dictionary.
    """
    step["start_time"] = time.time()
    step.setdefault("metrics", {})
    
    try:
        # Call the internal dummy action runner
        result = _execute_action(step, shared_context)

        # Capture provider stats from the DummyResult object
        if hasattr(result, "token_usage"):
            step["metrics"]["tokens"] = result.token_usage
        if hasattr(result, "latency"):
            step["metrics"]["latency"] = result.latency
        if hasattr(result, "cost_usd"):
            step["metrics"]["cost_usd"] = result.cost_usd

        step["status"] = "✅"
        step["message"] = getattr(result, "message", "")

    except Exception as e:
        step["status"] = "❌"
        step["message"] = str(e)

    finally:
        step["end_time"] = time.time()
        step["duration_sec"] = round(step["end_time"] - step["start_time"], 2)

    return step