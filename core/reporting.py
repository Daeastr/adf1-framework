# core/reporting.py
from pathlib import Path

def generate_run_summary(run_results: list) -> str:
    """
    Generates a Markdown summary of an orchestrator run.

    Args:
        run_results: A list of result dictionaries, one for each step.
    
    Returns:
        A Markdown-formatted string summarizing the run.
    """
    lines = ["### Orchestrator Run Summary", "---"]
    total_duration = 0.0
    errors = 0

    if not run_results:
        lines.append("No steps were executed.")
        return "\n".join(lines)

    for i, step_result in enumerate(run_results):
        step_id = step_result.get("id", f"step-{i+1}")
        status = step_result.get("status", "unknown").upper()
        duration = step_result.get("duration_sec", 0.0)
        total_duration += duration

        # Determine status icon
        icon = "✅" if status == "OK" else "❌"
        if status != "OK":
            errors += 1

        # This is the normal step summary line
        lines.append(f"**{icon} {step_id}** ({duration}s) - Status: `{status}`")
        
        # --- PATCH APPLIED HERE ---
        # Right after the normal summary, we bolt on the log pointer.
        if step_result.get("log_file"):
            # Keep PR comment lean — show filename only
            lines.append(f"  ↳ Log saved to artifacts: `{Path(step_result['log_file']).name}`")
        # --- END PATCH ---

    # Add a final summary line
    summary_icon = "✅" if errors == 0 else "❌"
    lines.insert(2, f"**{summary_icon} Overall Status:** {len(run_results)} steps completed in {total_duration:.2f}s with {errors} errors.\n")

    return "\n".join(lines)

# Example Usage (for demonstration):
if __name__ == '__main__':
    mock_run_results = [
        {
            "id": "t-init",
            "status": "ok",
            "duration_sec": 0.01,
            "log_file": "orchestrator_artifacts/t-init_step0.log"
        },
        {
            "id": "t-process",
            "status": "ok",
            "duration_sec": 0.52,
            "log_file": "orchestrator_artifacts/t-process_step1.log"
        },
        {
            "id": "t-finalize-failed",
            "status": "error",
            "message": "Finalization service unavailable",
            "duration_sec": 2.15,
            "log_file": "orchestrator_artifacts/t-finalize-failed_step2.log"
        }
    ]
    report = generate_run_summary(mock_run_results)
    print(report)