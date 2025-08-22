# core/reporting.py
import os
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

        # Build the summary line for this step
        lines.append(f"**{icon} {step_id}** ({duration}s) - Status: `{status}`")
        
        # --- PATCH APPLIED HERE ---
        # The previous simple log pointer is replaced with this CI-aware version.
        if step_result.get("log_file"):
            filename = Path(step_result["log_file"]).name
            run_id = os.getenv("GITHUB_RUN_ID")
            repo = os.getenv("GITHUB_REPOSITORY")  # e.g., "Daeastr/adf1-framework"
            
            if run_id and repo:
                # If running in CI, build a direct link to the run's artifact list.
                # The log file is inside the orchestrator-step-logs.zip artifact.
                url = f"https://github.com/{repo}/actions/runs/{run_id}"
                lines.append(f"  ↳ [Log saved to artifacts: {filename}]({url})")
            else:
                # Fallback to the plain filename if not in a CI context (e.g., local run).
                lines.append(f"  ↳ Log saved to artifacts: `{filename}`")
        # --- END PATCH ---

    # Add a final summary line
    summary_icon = "✅" if errors == 0 else "❌"
    lines.insert(2, f"**{summary_icon} Overall Status:** {len(run_results)} steps completed in {total_duration:.2f}s with {errors} errors.\n")

    return "\n".join(lines)

# Example Usage (for demonstration):
if __name__ == '__main__':
    # This will demonstrate the fallback behavior since GITHUB_RUN_ID will not be set.
    mock_run_results = [
        {
            "id": "t-init",
            "status": "ok",
            "duration_sec": 0.01,
            "log_file": "orchestrator_artifacts/t-init_step0.log"
        },
        {
            "id": "t-process-ok",
            "status": "ok",
            "duration_sec": 0.52,
            "log_file": "orchestrator_artifacts/t-process-ok_step1.log"
        }
    ]
    report = generate_run_summary(mock_run_results)
    print("--- Local Run Report (Fallback Behavior) ---")
    print(report)

    # To demonstrate the CI behavior, we can temporarily set the env vars
    print("\n--- CI Run Report (Simulated Behavior) ---")
    os.environ["GITHUB_RUN_ID"] = "123456789"
    os.environ["GITHUB_REPOSITORY"] = "Daeastr/adf1-framework"
    report_ci = generate_run_summary(mock_run_results)
    print(report_ci)
    del os.environ["GITHUB_RUN_ID"]
    del os.environ["GITHUB_REPOSITORY"]