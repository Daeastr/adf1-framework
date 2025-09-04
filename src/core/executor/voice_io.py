import logging
import time
from pathlib import Path
from src.core.providers.translate import translate_text

logger = logging.getLogger(__name__)
ARTIFACTS_DIR = Path("orchestrator_artifacts")

def handle_spoken_input(spoken_text: str, target_lang: str) -> str:
    """
    Process spoken input: translate, log metrics, and return translated text.
    """
    start_time = time.perf_counter()
    translated = translate_text(spoken_text, target_lang)
    latency = round(time.perf_counter() - start_time, 3)

    # Build metrics record
    metrics = {
        "input_text": spoken_text,
        "target_lang": target_lang,
        "translated_text": translated,
        "latency_sec": latency,
        "provider": "gemini",  # or dynamic from settings
        "success": not translated.endswith("[translation failed]")
    }

    # Log to cockpit
    logger.info(f"[voice_io] {metrics}")

    # Persist to orchestrator_artifacts for PR previews / replay
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    with open(ARTIFACTS_DIR / "translation_metrics.log", "a", encoding="utf-8") as f:
        f.write(f"{metrics}\n")

    return translated
