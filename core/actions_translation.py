# core/actions_translation.py
from core.orchestrator import register_action, call_action
from datetime import datetime, timezone
from core.translation_engine import get_engine
import logging

logger = logging.getLogger(__name__)

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

@register_action("translation_process")
def translation_process(context):
    """
    Delegates to `translate_text` for single or batch translation.
    Still uses the mock engine for reproducibility.
    """
    # Single text mode
    if "text" in context:
        return call_action("translate_text", context)

    # Batch mode
    if "batch" in context and isinstance(context["batch"], list):
        results = []
        for text in context["batch"]:
            batch_ctx = dict(context, text=text)
            results.append(call_action("translate_text", batch_ctx))
        return {"status": "ok", "results": results}

    return {"status": "error", "message": "No text or batch provided"}

@register_action("translate_text")
def translate_text(context):
    text = context.get("text", "")
    src = context.get("source_language", "en")
    tgt = context.get("target_language", "es")
    glossary = context.get("glossary", {})

    logger.info("[translate_text] Entry: src=%s tgt=%s text=%r", src, tgt, text)
    engine = get_engine(context.get("engine", "mock"), context)
    result = engine.translate(text, src, tgt, glossary)
    payload = {
        "status": "ok",
        "original": result.original,
        "translated": result.translated,
        "source_language": result.source_language,
        "target_language": result.target_language,
        "confidence": result.confidence,
    }
    logger.info("[translate_text] Exit: %s", payload)
    return payload