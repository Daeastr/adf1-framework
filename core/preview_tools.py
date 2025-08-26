from pathlib import Path
from typing import List, Dict, Any

def generate_batch_preview(instruction_id: str, segments: List[Dict[str, Any]]) -> Path:
    """
    Build a Markdown batch preview file from multiple translation segments.
    Returns the Path to the created file.
    """
    lines = [f"# Translation Batch Preview — {instruction_id}\n"]
    for seg in segments:
        src = seg.get("text") or seg.get("original", "")
        tgt = seg.get("translated", "")
        lines.append(f"**Source:** {src}")
        lines.append(f"**Translated:** {tgt}")
        if "confidence" in seg and seg["confidence"] is not None:
            lines.append(f"_Confidence:_ {seg['confidence']:.2%}")
        lines.append("\n---\n")
    path = Path("orchestrator_artifacts") / f"{instruction_id}_batch.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path

