# core/translation_engine.py
import logging
from dataclasses import dataclass
from typing import Dict, Optional

# --- New Provider-Agnostic Wrapper ---

class SafeTranslateClient:
    """
    Wraps a live translation provider with:
      - Stub fallback when no key or provider fails
      - Consistent logging to cockpit artifacts
      - Mock-friendly design for CI
    """

    def __init__(self, provider_cls=None, api_key: Optional[str] = None):
        self.api_key = api_key
        self.provider_cls = provider_cls
        self.provider = None

        if self.api_key and self.provider_cls:
            try:
                self.provider = self.provider_cls(api_key=self.api_key)
                logging.info("[SafeTranslateClient] Live provider initialised")
            except Exception as e:
                logging.warning(f"[SafeTranslateClient] Failed to init provider: {e}")
        else:
            logging.info("[SafeTranslateClient] Running in stub mode")

    def translate(self, source_lang: str, target_lang: str, text: str) -> str:
        """
        Attempts live translation; falls back to echo stub with markers.
        """
        if self.provider:
            try:
                # Assuming the real provider has a method with this signature
                return self.provider.translate(
                    text=text, source_language=source_lang, target_language=target_lang
                )
            except Exception as e:
                logging.error(f"[SafeTranslateClient] Live call failed: {e}")

        # Fallback path — tagged for easy cockpit filtering
        return f"[STUB:{source_lang}->{target_lang}] {text}"


# --- Existing Engine Logic ---

@dataclass
class TranslationResult:
    """Standardized output for all translation engines."""
    original: str
    translated: str
    source_language: str
    target_language: str
    confidence: float

class TranslationEngine:
    """Abstract base class for translation engines."""
    def translate(
        self,
        text: str,
        src: str,
        tgt: str,
        glossary: Optional[Dict[str, str]] = None
    ) -> TranslationResult:
        raise NotImplementedError("Subclasses must implement the translate method.")

class MockEngine(TranslationEngine):
    """A mock engine for testing and offline development."""
    def translate(
        self,
        text: str,
        src: str,
        tgt: str,
        glossary: Optional[Dict[str, str]] = None
    ) -> TranslationResult:
        translated_text = text
        if glossary:
            for term, replacement in glossary.items():
                translated_text = translated_text.replace(term, replacement)
        translated_text = translated_text[::-1]
        return TranslationResult(
            original=text,
            translated=f"[MOCK from {src} to {tgt}] {translated_text}",
            source_language=src,
            target_language=tgt,
            confidence=0.99
        )

class GeminiEngine(TranslationEngine):
    """A real engine powered by a Gemini provider (placeholder)."""
    def translate(
        self,
        text: str,
        src: str,
        tgt: str,
        glossary: Optional[Dict[str, str]] = None
    ) -> TranslationResult:
        return TranslationResult(
            original=text,
            translated=f"[GEMINI SIMULATION from {src} to {tgt}] {text}",
            source_language=src,
            target_language=tgt,
            confidence=0.95
        )

def get_engine(name: str, context: dict) -> TranslationEngine:
    """Factory function to get a translation engine instance."""
    if name.lower() == "gemini":
        return GeminiEngine()
    return MockEngine()