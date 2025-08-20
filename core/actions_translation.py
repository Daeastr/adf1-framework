# core/actions_translation.py
from core.orchestrator import register_action
from datetime import datetime, timezone

def _create_meta_block():
    """Helper to create a standardized metadata block for action returns."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": "demo-dry-run-01",  # Static for this demo
        "actor": "orchestrator"
    }

@register_action("translation_init")
def translation_init(context):
    """Stub handler for translation_init — safe placeholder."""
    return {
        "status": "ok",
        "data": {
            "source_language": None,
            "target_language": None,
            "translation_service": "default",
            "confidence_threshold": 0.8
        },
        "meta": _create_meta_block()
    }

@register_action("translate_text")
def translate_text(params, context):
    """
    Mock translation: reverses the text and tags it with a marker.
    Safe offline demo for cockpit visibility.
    """
    text = params.get("text", "")
    source = context.get("source_language", "en")
    target = context.get("target_language", "es")
    translated = text[::-1]  # reverse string for mock demo
    return {
        "status": "ok",
        "original": text,
        "translated": f"[MOCK from {source} to {target}] {translated}",
        "source_language": source,
        "target_language": target,
        "confidence": 0.95,
        "meta": _create_meta_block()
    }