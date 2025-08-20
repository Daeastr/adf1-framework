# tests/test_translate_text_real.py
from core.orchestrator import call_action, create_context

def test_translate_text_real_mock():
    ctx = create_context(
        text="Good morning",
        source_language="en",
        target_language="es",
        engine="mock",
        glossary={"morning": "mañana"}
    )
    out = call_action("translate_text", ctx)
    assert out["status"] == "ok"
    assert "mañana" in out["translated"]
    assert out["target_language"] == "es"
