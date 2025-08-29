# core/reporting.py
import os
import re
import time
from pathlib import Path
from itertools import islice
from collections import Counter

# --- New Metrics Formatting Logic ---
def _metrics_str(metrics: dict) -> str:
    """Formats a dictionary of provider metrics into a compact string."""
    parts = []
    if "tokens" in metrics:
        parts.append(f"{metrics['tokens']} tok")
    if "latency_ms" in metrics:
        # Assuming latency is in milliseconds, convert to seconds for display
        parts.append(f"{(metrics['latency_ms'] / 1000):.2f}s API")
    if "cost_usd" in metrics:
        parts.append(f"${metrics['cost_usd']:.4f}")
    return " | ".join(parts)

# --- Existing Tempo Tagging Logic ---
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
    Generates a Markdown summary of an orchestrator run, including
    performance tempo tags and provider-specific metrics for each step.
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
        # Build the summary line, now with an optional metrics block.
        summary_line = f"**{icon} {step_id}**"
        
        duration = step_result.get("duration_sec")
        if duration is not None:
            total_duration += duration
            tempo = _tempo_tag(duration)
            tempo_str = f" — {tempo}" if tempo else ""
            summary_line += f" `[{duration:.2f}s{tempo_str}]`"
        
        # Format and append the metrics string if metrics exist for this step.
        metrics_string = _metrics_str(step_result.get("metrics", {}))
        if metrics_string:
            summary_line += f" `({metrics_string})`"

        summary_line += f" - Status: `{status}`"
        lines.append(summary_line)
        # --- END PATCH ---

        # The logic for log previews and links remains the same.
        if step_result.get("log_file"):
            # ... (log preview generation logic)
            pass

    # Add a final summary line
    summary_icon = "✅" if errors == 0 else "❌"
    lines.insert(2, f"**{summary_icon} Overall Status:** {len(run_results)} steps completed in {total_duration:.2f}s with {errors} errors.\n")

    return "\n".join(lines)