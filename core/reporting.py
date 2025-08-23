# core/reporting.py
import os
import re
import time
from pathlib import Path
from itertools import islice
from collections import Counter

# ... (All helper functions: SPEED_COLORS, format_speed_tag, classify_speed, _highlight_severity, _preview_log, aggregate_by_tier, render_aggregation_table) ...

SPEED_COLORS = { "FAST": "\033[92m", "SLOW": "\033[91m" }
RESET = "\033[0m"
FAST_THRESHOLD = 1.0
SLOW_THRESHOLD = 5.0
HIGHLIGHT_PATTERNS = {
    r"\bERROR\b": "🔴 ERROR",
    r"\bWARNING\b": "🟡 WARNING",
    r"\bFAIL(?:ED|URE)?\b": "🔴 FAIL"
}

def format_speed_tag(tag: str) -> str:
    return f"{SPEED_COLORS.get(tag, '')}{tag}{RESET}" if tag else ""

def classify_speed(elapsed_seconds: float) -> str:
    if elapsed_seconds <= FAST_THRESHOLD: return "FAST"
    if elapsed_seconds >= SLOW_THRESHOLD: return "SLOW"
    return ""

def _highlight_severity(text: str) -> str:
    for pattern, replacement in HIGHLIGHT_PATTERNS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def _preview_log(path: str, lines: int = 3, collapse_after: int = 5) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = [line.rstrip("\n") for line in f]
        all_lines = [_highlight_severity(line) for line in all_lines]
        if len(all_lines) > collapse_after:
            preview_text = "\n".join(all_lines[:collapse_after])
            return f"<details><summary>Preview first {collapse_after} lines</summary>\n\n```\n{preview_text}\n```\n\n</details>"
        else:
            preview_text = "\n".join(all_lines[:lines])
            return f"```\n{preview_text}\n```"
    except OSError:
        return ""

def aggregate_by_tier(steps):
    steps = list(steps)
    total = len(steps) or 1
    counts = Counter()
    for s in steps:
        tier = (s.get("performance_tier") or "").upper()
        severity = (s.get("severity") or "").upper()
        if tier in ("FAST", "SLOW"): counts[tier] += 1
        if severity and severity not in ("OK", "FAST", "SLOW"): counts[severity] += 1
    pct = lambda c: round((c / total) * 100, 1)
    return [
        {"label": "🟢 FAST", "count": counts.get("FAST", 0), "pct": pct(counts.get("FAST", 0))},
        {"label": "🔴 SLOW", "count": counts.get("SLOW", 0), "pct": pct(counts.get("SLOW", 0))},
        {"label": "⚠️ WARNINGS", "count": counts.get("WARNING", 0), "pct": pct(counts.get("WARNING", 0))},
        {"label": "🔴 ERROR/FAIL", "count": counts.get("ERROR", 0) + counts.get("FAIL", 0), "pct": pct(counts.get("ERROR", 0) + counts.get("FAIL", 0))},
    ]

def render_aggregation_table(rows):
    md = ["\n### 🗂️ Summary\n", "| Tier / Severity | Count | % of Steps |", "|-----------------|-------|------------|"]
    for r in rows:
        md.append(f"| {r['label']} | {r['count']} | {r['pct']}% |")
    return "\n".join(md) + "\n"

# --- Main Reporting Function ---

def generate_run_summary(run_results: list) -> str:
    """
    Generates a full Markdown summary, including an aggregation table and
    step-by-step details with log previews.
    """
    header_text = "###  orchestrator Run Summary\n---"

    if not run_results:
        return f"{header_text}\nNo steps were executed."

    # --- 1. Enrich raw results for aggregation ---
    enriched_steps = []
    for result in run_results:
        duration = result.get("duration_sec", 0.0)
        enriched_steps.append({
            "severity": result.get("status", "unknown"),
            "performance_tier": classify_speed(duration),
        })

    # --- 2. Build the per-step details section ---
    per_step_lines = ["\n### 📋 Step Details\n"]
    for i, step_result in enumerate(run_results):
        step_id = step_result.get("id", f"step-{i+1}")
        status = step_result.get("status", "unknown").upper()
        duration = step_result.get("duration_sec", 0.0)
        icon = "✅" if status == "OK" else "❌"

        per_step_lines.append(f"**{icon} {step_id}** ({duration:.2f}s) - Status: `{status}`")
        
        if step_result.get("log_file"):
            filename = Path(step_result["log_file"]).name
            run_id = os.getenv("GITHUB_RUN_ID")
            repo = os.getenv("GITHUB_REPOSITORY")
            preview = _preview_log(step_result["log_file"])

            if run_id and repo:
                url = f"https://github.com/{repo}/actions/runs/{run_id}"
                per_step_lines.append(f"  ↳ [Log saved to artifacts: {filename}]({url})")
            else:
                per_step_lines.append(f"  ↳ Log saved to artifacts: `{filename}`")
            
            if preview:
                per_step_lines.append(f"    {preview}")
    
    per_step_section = "\n".join(per_step_lines)

    # --- 3. Weave the final comment body together ---
    summary_rows = aggregate_by_tier(enriched_steps)
    comment_body = "\n".join([
        header_text,
        render_aggregation_table(summary_rows),
        per_step_section,
    ])
    
    return comment_body