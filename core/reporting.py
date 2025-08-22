# core/reporting.py
import os
import re
from pathlib import Path
from itertools import islice

# --- New Severity Highlighting Logic ---

HIGHLIGHT_PATTERNS = {
    r"\bERROR\b": "🔴 ERROR",
    r"\bWARNING\b": "🟡 WARNING",
    r"\bFAIL(?:ED|URE)?\b": "🔴 FAIL"
}

def _highlight_severity(text: str) -> str:
    """Replace severity keywords with emoji-tagged versions."""
    for pattern, replacement in HIGHLIGHT_PATTERNS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

# --- Existing Helper Functions ---

def _preview_log(path: str, lines: int = 3, collapse_after: int = 5) -> str:
    """Return the first N lines from a log file; collapse if it exceeds collapse_after."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = [line.rstrip("\n") for line in f]
        
        # Apply highlighting to each line before making formatting decisions
        all_lines = [_highlight_severity(line) for line in all_lines]
        
        if len(all_lines) > collapse_after:
            preview_text = "\n".join(all_lines[:collapse_after])
            return (
                f"<details><summary>Preview first {collapse_after} lines</summary>\n\n"
                f"```\n{preview_text}\n```\n\n</details>"
            )
        else:
            preview_text = "\n".join(all_lines[:lines])
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
            
            preview = _preview_log(step_result["log_file"], lines=3, collapse_after=5)

            if run_id and repo:
                url = f"https://github.com/{repo}/actions/runs/{run_id}"
                lines.append(f"  ↳ [Log saved to artifacts: {filename}]({url})")
            else:
                lines.append(f"  ↳ Log saved to artifacts: `{filename}`")
            
            if preview:
                lines.append(f"    {preview}")

    summary_icon = "✅" if errors == 0 else "❌"
    lines.insert(2, f"**{summary_icon} Overall Status:** {len(run_results)} steps completed in {total_duration:.2f}s with {errors} errors.\n")

    return "\n".join(lines)

# Example Usage (for demonstration):
if __name__ == '__main__':
    # Create a dummy log file with severity keywords to test highlighting
    artifacts_dir = Path("orchestrator_artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    highlight_log_path = artifacts_dir / "highlight.log"
    highlight_log_path.write_text('Line 1: All good\nLine 2: A minor WARNING occurred\nLine 3: Critical ERROR detected')
    
    mock_run_results = [
        {"id": "highlight-test-step", "status": "error", "duration_sec": 0.1, "log_file": str(highlight_log_path)}
    ]
    
    print("--- Report with Severity Highlighting ---")
    report = generate_run_summary(mock_run_results)
    print(report)

    # Clean up dummy file
    highlight_log_path.unlink()