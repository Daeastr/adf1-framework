# core/reporting.py
import os
from pathlib import Path
from itertools import islice

# --- New Helper Function ---

def _preview_log(path: str, lines: int = 3, collapse_after: int = 5) -> str:
    """Return the first N lines from a log file; collapse if it exceeds collapse_after."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            # Read all lines to check the total count
            head = [line.rstrip("\n") for line in f]
        
        if len(head) > collapse_after:
            # If the log is long, create a collapsible section
            preview_text = "\n".join(head[:collapse_after])
            return f"<details><summary>Preview first {collapse_after} lines</summary>\n\n```\n{preview_text}\n```\n\n</details>"
        else:
            # If the log is short, show a simple code block
            preview_text = "\n".join(head[:lines])
            return f"```\n{preview_text}\n```"
    except OSError:
        return ""


# --- Main Reporting Logic ---

def generate_run_summary(run_results: list) -> str:
    """
    Generates a Markdown summary of an orchestrator run, including log previews.
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
        
        if step_result.get("log_file"):
            filename = Path(step_result["log_file"]).name
            run_id = os.getenv("GITHUB_RUN_ID")
            repo = os.getenv("GITHUB_REPOSITORY")
            
            # The preview is now pre-formatted by the helper function.
            preview = _preview_log(step_result["log_file"], lines=3, collapse_after=5)

            # Append the link to the full artifact.
            if run_id and repo:
                url = f"https://github.com/{repo}/actions/runs/{run_id}"
                lines.append(f"  ↳ [Log saved to artifacts: {filename}]({url})")
            else:
                lines.append(f"  ↳ Log saved to artifacts: `{filename}`")
            
            # Append the pre-formatted preview block directly.
            if preview:
                lines.append(f"    {preview}")

    summary_icon = "✅" if errors == 0 else "❌"
    lines.insert(2, f"**{summary_icon} Overall Status:** {len(run_results)} steps completed in {total_duration:.2f}s with {errors} errors.\n")

    return "\n".join(lines)

# Example Usage (for demonstration):
if __name__ == '__main__':
    # Create dummy log files to test both short and long previews
    artifacts_dir = Path("orchestrator_artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    short_log_path = artifacts_dir / "short.log"
    long_log_path = artifacts_dir / "long.log"
    short_log_path.write_text('Line 1\nLine 2\nLine 3')
    long_log_path.write_text('Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7')
    
    mock_run_results = [
        {"id": "short-log-step", "status": "ok", "duration_sec": 0.1, "log_file": str(short_log_path)},
        {"id": "long-log-step", "status": "ok", "duration_sec": 0.2, "log_file": str(long_log_path)}
    ]
    
    print("--- Report with Collapsible Preview ---")
    report = generate_run_summary(mock_run_results)
    print(report)

    # Clean up dummy files
    short_log_path.unlink()
    long_log_path.unlink()