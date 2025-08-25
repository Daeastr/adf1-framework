import time
import json
from pathlib import Path

# The orchestrator's core logic for running steps
from .executor import run_agent_task
# Import the actual implementations from their new, non-circular location
from .action_manager import call_action as _call_action_impl
from .action_manager import create_context as _create_context_impl

# This import is critical to ensure that all decorated actions in the
# translation module are registered with the action manager when the app starts.
import core.actions_translation

def execute_instruction_plan(instruction: dict) -> list:
    """
    The main logic for running a multi-step instruction plan. It initializes
    a shared context and iterates through each step, calling the executor.
    """
    shared_context = create_context() # Uses the re-exported function below
    results = []

    steps = instruction.get("steps", [])
    for i, step in enumerate(steps):
        step["_step_index"] = i
        result = run_agent_task(step, shared_context)
        if result.get("status") == "ok":
            shared_context.update(result.get("data", {}))
        results.append(result)
        
    return results

def run_instruction(instruction: dict):
    """

    Routes an instruction to the sandbox runner if the 'sandbox' flag is set,
    otherwise executes it through the standard plan executor.
    """
    if instruction.get("sandbox"):
        from core.sandbox_runner import run_in_sandbox
        return run_in_sandbox(instruction)
    return execute_instruction_plan(instruction)

# --- Backward Compatibility Wrappers ---
# These functions re-export the real implementations from the action_manager,
# ensuring that any older test or module that still imports them from this
# file will continue to work without needing to be refactored immediately.

def call_action(*args, **kwargs):
    """A stable alias that points to the real call_action implementation."""
    return _call_action_impl(*args, **kwargs)

def create_context(*args, **kwargs):
    """A stable alias that points to the real create_context implementation."""
    return _create_context_impl(*args, **kwargs)