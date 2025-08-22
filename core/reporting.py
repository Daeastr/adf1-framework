# core/reporting.py
import os
from pathlib import Path
from itertools import islice

# --- New Helper Function ---

def _preview_log(path: str, lines: int = 3) -> str:
    """Return the first N lines from a log file, trimmed for PR display."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            head = list(islice(f, lines))
        # Strip trailing newlines/spaces for clean embedding
        return "".join(head).strip()
    except OSError:
        return ""

# --- Main Reporting Logic ---

def generate_run_summary(run_results: list) -> str:
    """
    Generates a Markdown summary of an orchestrator run, including log previews.

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

        icon = "✅" if status == "OK" else "❌"
        if status != "OK":
            errors += 1

        lines.append(f"**{icon} {step_id}** ({duration}s) - Status: `{status}`")
        
        # --- PATCH APPLIED HERE ---
        # This block now also extracts and appends a log preview.
        if step_result.get("log_file"):
            filename = Path(step_result["log_file"]).name
            run_id = os.getenv("GITHUB_RUN_ID")
            repo = os.getenv("GITHUB_REPOSITORY")
            
            # Extract a preview from the log file.
            preview = _preview_log(step_result["log_file"], lines=3)

            # Append the link to the full artifact.
            if run_id and repo:
                url = f"https://github.com/{repo}/actions/runs/{run_id}"
                lines.append(f"  ↳ [Log saved to artifacts: {filename}]({url})")
            else:
                lines.append(f"  ↳ Log saved to artifacts: `{filename}`")
            
            # If a preview was extracted, append it in a code block.
            if preview:
                lines.append(f"    ```\n{preview}\n    ```")
        # --- END PATCH ---

    summary_icon = "✅" if errors == 0 else "❌"
    lines.insert(2, f"**{summary_icon} Overall Status:** {len(run_results)} steps completed in {total_duration:.2f}s with {errors} errors.\n")

    return "\n".join(lines)

# Example Usage (for demonstration):
if __name__ == '__main__':
    # Create dummy log files for the preview function to read
    artifacts_dir = Path("orchestrator_artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    log1_path = artifacts_dir / "t-init_step0.log"
    log2_path = artifacts_dir / "t-process-ok_step1.log"
    log1_path.write_text('{\n  "status": "ok",\n  "data": {')
    log2_path.write_text('{\n  "status": "ok",\n  "original": "Hello World",\n ...')
    
    mock_run_results = [
        {"id": "t-init", "status": "ok", "duration_sec": 0.01, "log_file": str(log1_path)},
        {"id": "t-process-ok", "status": "ok", "duration_sec": 0.52, "log_file": str(log2_path)}
    ]
    
    print("--- Local Run Report (with log previews) ---")
    report = generate_run_summary(mock_run_results)
    print(report)

    # Clean up dummy files
    log1_path.unlink()
    log2_path.unlink()