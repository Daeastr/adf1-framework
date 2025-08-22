# scripts/dry_run_log_demo.py
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

from core.executor import run_agent_task

# This demo assumes a 'noop' action is registered in your orchestrator.
# If not, replace 'noop' with another safe, registered stub action
# like 'translation_init'.
#
# Also, the run_agent_task from our previous step takes a shared_context.
# We will pass an empty one for this simple demo.

demo_task = {
    "id": "log-demo-001",
    "action": "translation_init",  # Using a known safe stub action
    "params": {},
    "_step_index": 1
}

print(f"Running demo task: {demo_task['id']}")
result = run_agent_task(demo_task, shared_context={})
print("\nReturned result:")
print(result)

print(f"\nLog file created at: {result.get('log_file')}")