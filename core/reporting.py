# core/reporting.py

FAST_THRESHOLD = 1.0   # seconds
SLOW_THRESHOLD = 3.0   # seconds

def _tempo_tag(elapsed: float) -> str:
    if elapsed >= SLOW_THRESHOLD:
        return "🟡 SLOW"
    elif elapsed <= FAST_THRESHOLD:
        return "🟢 FAST"
    return ""

def _metrics_str(metrics: dict) -> str:
    parts = []
    if metrics.get("tokens") is not None:
        parts.append(f"{metrics['tokens']} tok")
    if metrics.get("latency") is not None:
        parts.append(f"{metrics['latency']:.2f}s API")
    if metrics.get("cost_usd") is not None:
        parts.append(f"${metrics['cost_usd']:.4f}")
    return " | ".join(parts)

def build_preview_lines(steps: list) -> list:
    lines = []
    for step in steps:
        status = step.get("status", "❓")
        name = step.get("name", "unknown")
        message = step.get("message", "")
        if step.get("start_time") and step.get("end_time"):
            elapsed = step["end_time"] - step["start_time"]
            tempo = _tempo_tag(elapsed)
            metrics_str = _metrics_str(step.get("metrics", {}))
            if metrics_str:
                lines.append(f"{status} {name} [{elapsed:.2f}s — {tempo}] ({metrics_str}) — {message}")
            else:
                lines.append(f"{status} {name} [{elapsed:.2f}s — {tempo}] — {message}")
        else:
            lines.append(f"{status} {name} — {message}")
    return lines
