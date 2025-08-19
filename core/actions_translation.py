# core/actions_translation.py
from core.orchestrator import register_action

@register_action("translate_text")
def translate_text(context):
    text = context.get("text", "")
    src_lang = context.get("source_language", "en")
    tgt_lang = context.get("target_language", "es")

    # Mock transform — reverse text and mark as MOCKED
    translated = f"[MOCKED from {src_lang} to {tgt_lang}] {text[::-1]}"

    return {
        "status": "ok",
        "original": text,
        "translated": translated,
        "source_language": src_lang,
        "target_language": tgt_lang,
        "confidence": 0.95
    }