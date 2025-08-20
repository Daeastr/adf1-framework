from core.orchestrator import call_action, create_context

def test_translation_process_single():
    ctx = create_context(text="Good morning", source_language="en", target_language="es", engine="mock")
    out = call_action("translation_process", ctx)
    assert out["status"] == "ok"
    assert "translated" in out

def test_translation_process_batch():
    ctx = create_context(batch=["One", "Two"], source_language="en", target_language="es", engine="mock")
    out = call_action("translation_process", ctx)
    assert out["status"] == "ok"
    assert len(out["results"]) == 2