def render_step_badges(step: dict) -> str:
    """Render priority and risk badges for a step, matching render_step_summary conventions."""
    badges = []
    
    # Priority badge - using _priority key to match render_step_summary
    priority = step.get("_priority", "medium")
    p = priority.capitalize()
    color = {"Low": "brightgreen", "Medium": "yellow", "High": "red"}.get(p, "lightgrey")
    badges.append(f"![Priority: {p}](https://img.shields.io/badge/Priority-{p}-{color})")
    
    # Risk badge - using _risk key to match render_step_summary  
    risk = step.get("_risk", "review")
    r = risk.capitalize()
    color = {"Safe": "brightgreen", "Review": "yellow", "Critical": "red"}.get(r, "lightgrey")
    badges.append(f"![Risk: {r}](https://img.shields.io/badge/Risk-{r}-{color})")
    
    return " ".join(badges)
