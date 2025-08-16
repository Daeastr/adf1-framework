def render_step_badges(step: dict) -> str:
    """Render priority and risk badges for a step, matching render_step_summary conventions."""
    badges = []
    
    # Metadata badges - matching render_step_summary exactly
    priority = step.get("_priority", "medium").capitalize()
    risk = step.get("_risk", "review").capitalize()
    
    # Priority badge
    color = {"Low": "brightgreen", "Medium": "yellow", "High": "red"}.get(priority, "lightgrey")
    badges.append(f"![Priority: {priority}](https://img.shields.io/badge/Priority-{priority}-{color})")
    
    # Risk badge
    color = {"Safe": "brightgreen", "Review": "yellow", "Critical": "red"}.get(risk, "lightgrey")
    badges.append(f"![Risk: {risk}](https://img.shields.io/badge/Risk-{risk}-{color})")
    
    return " ".join(badges)
