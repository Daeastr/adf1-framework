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