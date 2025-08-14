import uuid, time
from pathlib import Path

ARTIFACTS_DIR = Path("orchestrator_artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

def _save_step_log(task_id: str, step_idx: int, content: str) -> str:
    filename = f"{task_id}_step{step_idx}.log"
    path = ARTIFACTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(path)

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
