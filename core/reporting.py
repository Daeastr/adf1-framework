"""
Reporting functions for step summaries and badges.
"""
from typing import Dict, Any


def render_step_summary(step: Dict[str, Any]) -> str:
    """Render a step summary with metadata and logs."""
    lines = []
    lines.append(f"### 🧩 Step {step['id']} — {step['action']}")

    # Metadata badges - updated format
    priority = step.get("priority", "unknown").capitalize()
    risk = step.get("risk", "unknown").capitalize()
    lines.append(f"🧭 Priority: {priority} | 🚨 Risk: {risk}")

    # Capabilities display
    capabilities = step.get("_capabilities", [])
    if capabilities:
        lines.append(f"🔐 **Capabilities**: {', '.join(capabilities)}")

    # Existing output/logs
    if "duration_sec" in step:
        lines.append(f"⏱ Duration: {step['duration_sec']}s")
    if "log_file" in step:
        lines.append(f"[📄 Full Log]({step['log_file']})")

    return "\n".join(lines)


def render_step_badges(step: dict) -> str:
    """Render priority and risk badges for a step, matching render_step_summary conventions."""
    badges = []
    
    # Metadata badges - matching render_step_summary exactly
    priority = step.get("priority", "unknown").capitalize()
    risk = step.get("risk", "unknown").capitalize()
    
    # Priority badge
    color = {"Low": "brightgreen", "Medium": "yellow", "High": "red", "Unknown": "lightgrey"}.get(priority, "lightgrey")
    badges.append(f"![Priority: {priority}](https://img.shields.io/badge/Priority-{priority}-{color})")
    
    # Risk badge
    color = {"Safe": "brightgreen", "Review": "yellow", "Critical": "red", "Unknown": "lightgrey"}.get(risk, "lightgrey")
    badges.append(f"![Risk: {risk}](https://img.shields.io/badge/Risk-{risk}-{color})")
    
    return " ".join(badges)


def render_multiple_steps(steps: list) -> str:
    """Render summaries for multiple steps."""
    summaries = []
    for step in steps:
        summaries.append(render_step_summary(step))
    return "\n\n".join(summaries)