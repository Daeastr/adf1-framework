import time
import logging
from src.utils.config import settings
from src.core.providers import gemini  # adjust if your provider module name differs

logger = logging.getLogger(__name__)

def translate_text(text: str, target_lang: str) -> str:
    """
    Translate text to the target language with metrics logging and safe fallback.
    """
    provider_name = "gemini"
    start_time = time.perf_counter()

    try:
        # Call the provider's translate function
        translated = gemini.translate(text, target_lang)

        latency = time.perf_counter() - start_time
        metrics = {
            "provider": provider_name,
            "target_lang": target_lang,
            "success": True,
            "latency_sec": round(latency, 3),
            "tokens_used": getattr(translated, "tokens_used", None)
        }
        logger.info(f"[translate_text] {metrics}")

        # Return the translated string if present
        if isinstance(translated, str):
            return translated
        elif hasattr(translated, "text"):
            return translated.text
        else:
            return str(translated)

    except Exception as e:
        latency = time.perf_counter() - start_time
        metrics = {
            "provider": provider_name,
            "target_lang": target_lang,
            "success": False,
            "latency_sec": round(latency, 3),
            "error": str(e)
        }
        logger.error(f"[translate_text] {metrics}", exc_info=True)

        # Safe fallback: return original text with failure marker
        return f"{text} [translation failed]"
