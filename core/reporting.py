# core/reporting.py
import os
import re
import time
from pathlib import Path
from itertools import islice
from collections import Counter

# ... (functions format_speed_tag, classify_speed, format_log_line, HIGHLIGHT_PATTERNS, _highlight_severity, _preview_log remain the same) ...

# --- ANSI Color Formatting for Speed Tags ---

SPEED_COLORS = {
    "FAST": "\033[92m",   # green
    "SLOW": "\033[91m",   # red
}
RESET = "\033[0m"

def format_speed_tag(tag: str) -> str:
    """Wraps a speed tag in ANSI color codes for terminal display."""
    return f"{SPEED_COLORS.get(tag, '')}{tag}{RESET}" if tag else ""

# --- Helper for Formatted Live Logging with Speed Classification ---

# Thresholds in seconds for performance classification
FAST_THRESHOLD = 1.0
SLOW_THRESHOLD = 5.0

def classify_speed(elapsed_seconds: float) -> str:
    """Classifies the elapsed time into performance buckets."""
    if elapsed_seconds <= FAST_THRESHOLD:
        return "FAST"
    elif elapsed_seconds >= SLOW_THRESHOLD:
        return "SLOW"
    return ""  # Mid-range, no specific label needed

def format_log_line(step_name, status, message, start_time=None):
    """Formats a log line with status, timing, and a color-coded performance tag."""
    elapsed_label = ""
    if start_time:
        elapsed_seconds = time.time() - start_time
        speed_tag = classify_speed(elapsed_seconds)
        
        formatted_tag = format_speed_tag(speed_tag)
        
        label_str = f" [{elapsed_seconds:.2f}s]"
        if formatted_tag:
            label_str += f" {formatted_tag}"
        elapsed_label = label_str
        
    return f"{status} {step_name}{elapsed_label} — {message}"

# --- Severity Highlighting Logic (for Markdown) ---

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

# --- Helper Functions (for Markdown) ---

def _preview_log(path: str, lines: int = 3, collapse_after: int = 5) -> str:
    """Return the first N lines from a log file; collapse if it exceeds collapse_after."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = [line.rstrip("\n") for line in f]
        
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


# --- New Aggregation and Rendering Logic ---

def aggregate_by_tier(steps):
    """
    steps: iterable of dicts with keys: severity, elapsed, performance_tier
    Returns: dict with counts + % breakdown
    """
    step_list = list(steps)
    total = len(step_list) or 1
    counts = Counter()

    for s in step_list:
        tier = s.get("performance_tier", "").upper()
        severity = s.get("severity", "").upper()
        if tier in ("FAST", "SLOW"):
            counts[tier] += 1
        if severity in ("WARNING", "ERROR", "FAIL"):
            counts[severity] += 1

    def pct(count):
        return round((count / total) * 100, 1)

    return [
        {"label": "🟢 FAST", "count": counts.get("FAST", 0), "pct": pct(counts.get("FAST", 0))},
        {"label": "🔴 SLOW", "count": counts.get("SLOW", 0), "pct": pct(counts.get("SLOW", 0))},
        {"label": "⚠️ WARNINGS", "count": counts.get("WARNING", 0), "pct": pct(counts.get("WARNING", 0))},
        {"label": "🔴 ERROR/FAIL", "count": counts.get("ERROR", 0) + counts.get("FAIL", 0),
         "pct": pct(counts.get("ERROR", 0) + counts.get("FAIL", 0))},
    ]

def render_aggregation_table(rows):
    """Renders the aggregation data into a Markdown table."""
    md = ["\n### 🗂️ Summary\n", "| Tier / Severity | Count | % of Steps |", "|-----------------|-------|------------|"]
    for r in rows:
        md.append(f"| {r['label']} | {r['count']} | {r['pct']}% |")
    return "\n".join(md) + "\n"


# --- Main Reporting Function ---

def generate_run_summary(run_results: list) -> str:
    """
    Generates a full Markdown summary of an orchestrator run, including an
    aggregation table and step-by-step details with log previews.
    """
    header = "###  Orchestrator Run Summary"
    
    if not run_results:
        return f"{header}\n---\nNo steps were executed."

    # --- 1. Enrich data for aggregation ---
    enriched_steps = []
    for result in run_results:
        duration = result.get("duration_sec", 0.0)
        enriched_steps.append({
            "severity": result.get("status", "unknown"),
            "performance_tier": classify_speed(duration),
        })

    # --- 2. Generate the summary table ---
    summary_rows = aggregate_by_tier(enriched_steps)
    table_md = render_aggregation_table(summary_rows)

    # --- 3. Generate the detailed per-step section ---
    step_lines = ["\n### 📋 Step Details\n"]
    for i, step_result in enumerate(run_results):
        step_id = step_result.get("id", f"step-{i+1}")
        status = step_result.get("status", "unknown").upper()
        duration = step_result.get("duration_sec", 0.0)
        icon = "✅" if status == "OK" else "❌"

        step_lines.append(f"**{icon} {step_id}** ({duration}s) - Status: `{status}`")
        
        if step_result.get("log_file"):
            filename = Path(step_result["log_file"]).name
            run_id = os.getenv("GITHUB_RUN_ID")
            repo = os.getenv("GITHUB_REPOSITORY")
            preview = _preview_log(step_result["log_file"])

            if run_id and repo:
                url = f"https://github.com/{repo}/actions/runs/{run_id}"
                step_lines.append(f"  ↳ [Log saved to artifacts: {filename}]({url})")
            else:
                step_lines.append(f"  ↳ Log saved to artifacts: `{filename}`")
            
            if preview:
                step_lines.append(f"    {preview}")
    
    # --- 4. Combine all parts into the final report ---
    return "\n".join([header, "---", table_md, "\n".join(step_lines)])