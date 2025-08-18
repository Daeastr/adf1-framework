# core/actions.py
from pathlib import Path

ARTIFACTS_DIR = Path("orchestrator_artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

def _write_log(step_id: str, message: str) -> Path:
    p = ARTIFACTS_DIR / f"{step_id}.log"
    p.write_text(message, encoding="utf-8")
    return p

def run_action(step: dict, safe_mode: bool = True) -> tuple[bool, Path]:
    action = step.get("action", "noop")
    step_id = step.get("id", f"{action}")
    params = step.get("params", {})

    if action == "noop":
        log = _write_log(step_id, "noop: nothing to do")
        return True, log

    if action == "validate":
        # Placeholder: pretend we validated params
        log = _write_log(step_id, f"validate: params={params}")
        return True, log

    if action == "transform":
        src = params.get("source") or params.get("target") or params.get("glob") or "docs/"
        msg = f"transform: planned transform over {src}"
        if safe_mode:
            msg += " (dry-run)"
        log = _write_log(step_id, msg)
        return True, log

    if action == "apply_patch":
        diff = params.get("diff", "")
        msg = "apply_patch: captured diff"
        if safe_mode:
            msg += " (dry-run, not applied)"
        msg += f"\n---\n{diff}"
        log = _write_log(step_id, msg)
        return True, log

    if action == "create_endpoint":
        name = params.get("name", "endpoint")
        route = params.get("route", f"/{name}")
        msg = f"create_endpoint: would scaffold {name} at {route}"
        if safe_mode:
            msg += " (dry-run)"
        log = _write_log(step_id, msg)
        return True, log

    # Unknown actions are skipped gracefully
    log = _write_log(step_id, f"unknown action '{action}' (skipped)")
    return True, log
