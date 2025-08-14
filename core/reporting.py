if step.get("log_file"):
    lines.append(f"  [[📄 Full Log]]({step['log_file']})")
def render_step_badges(instruction: dict) -> str:
    badges = []
    if "priority" in instruction:
        p = instruction["priority"].capitalize()
        color = {"Low":"brightgreen","Medium":"yellow","High":"red"}.get(p, "lightgrey")
        badges.append(f"![Priority: {p}](https://img.shields.io/badge/Priority-{p}-{color})")
    if "risk" in instruction:
        r = instruction["risk"].capitalize()
        color = {"Safe":"brightgreen","Review":"yellow","Critical":"red"}.get(r, "lightgrey")
        badges.append(f"![Risk: {r}](https://img.shields.io/badge/Risk-{r}-{color})")
    return " ".join(badges)
