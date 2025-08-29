# core/reporting.py
import os
import re
import time
from pathlib import Path
from itertools import islice
from collections import Counter

# --- New Tempo Tagging Logic ---
FAST_THRESHOLD = 1.0   # seconds
SLOW_THRESHOLD = 3.0   # seconds

def _tempo_tag(elapsed: float) -> str:
    """Returns a visual tag based on performance thresholds."""
    if elapsed >= SLOW_THRESHOLD:
        return "🟡 SLOW"
    elif elapsed <= FAST_THRESHOLD:
        return "🟢 FAST"
    return ""

# ... (all other existing helper functions like _highlight_severity, _preview_log, etc. remain here) ...

# --- Main Reporting Logic ---

def generate_run_summary(run_results: list) -> str:
    """
    Generates a Markdown summary of an orchestrator run, now including
    performance tempo tags for each step.
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
        icon = "✅" if status == "OK" else "❌"
        if status != "OK":
            errors += 1

        # --- PATCH APPLIED HERE ---
        # Calculate elapsed time and generate a tempo tag for the summary line.
        summary_line = f"**{icon} {step_id}**"
        
        # The executor already calculates 'duration_sec', so we can use that directly.
        duration = step_result.get("duration_sec")
        if duration is not None:
            total_duration += duration
            tempo = _tempo_tag(duration)
            tempo_str = f" — {tempo}" if tempo else ""
            summary_line += f" `[{duration:.2f}s{tempo_str}]`"
        
        summary_line += f" - Status: `{status}`"
        lines.append(summary_line)
        # --- END PATCH ---

        # The logic for log previews and links remains the same.
        if step_result.get("log_file"):
            filename = Path(step_result["log_file"]).name
            run_id = os.getenv("GITHUB_RUN_ID")
            repo = os.getenv("GITHUB_REPOSITORY")
            preview = _preview_log(step_result["log_file"])

            if run_id and repo:
                url = f"https://github.com/{repo}/actions/runs/{run_id}"
                lines.append(f"  ↳ [Log saved to artifacts: {filename}]({url})")
            else:
                lines.append(f"  ↳ Log saved to artifacts: `{filename}`")
            
            if preview:
                lines.append(f"    {preview}")

    # Add a final summary line
    summary_icon = "✅" if errors == 0 else "❌"
    lines.insert(2, f"**{summary_icon} Overall Status:** {len(run_results)} steps completed in {total_duration:.2f}s with {errors} errors.\n")

    return "\n".join(lines)