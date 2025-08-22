# core/actions_translation.py
import os
import requests
import logging
from datetime import datetime, timezone
from core.orchestrator import register_action, call_action
from core.translation_engine import get_engine


logger = logging.getLogger(__name__)

# --- New Functionality: Dynamic Language Support ---

SUPPORTED_LANGS_STATIC = ["en", "es", "fr", "de"]

def get_supported_languages():
    api_key = os.getenv("GEMINI_API_KEY")
    provider_url = "https://api.gemini.example/v1/languages"  # swap to real endpoint

    if not api_key:
        logger.warning("[get_supported_languages] No API key — using static list")
        return SUPPORTED_LANGS_STATIC

    try:
        resp = requests.get(
            provider_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5
        )
        resp.raise_for_status()
        langs = resp.json().get("languages", [])
        logger.info("[get_supported_languages] Fetched %d languages", len(langs))
        return langs or SUPPORTED_LANGS_STATIC
    except Exception as e:
        logger.error("[get_supported_languages] Call failed: %s — fallback", e)
        return SUPPORTED_LANGS_STATIC


# --- Existing Actions ---

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

@register_action("set_translation_languages")
def set_translation_languages(context, source_lang, target_lang):
    """Stub or real setter for translation languages."""
    context["source_language"] = source_lang
    context["target_language"] = target_lang
    return {
        "status": "ok",
        "data": {
            "source_language": source_lang,
            "target_language": target_lang
        }
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