# core/translation_engine.py
from dataclasses import dataclass
from typing import Dict, Optional

# --- Data Contracts ---

@dataclass
class TranslationResult:
    """Standardized output for all translation engines."""
    original: str
    translated: str
    source_language: str
    target_language: str
    confidence: float

# --- Base Engine ---

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

# --- Concrete Implementations ---

class MockEngine(TranslationEngine):
    """A mock engine for testing and offline development."""
    def translate(
        self,
        text: str,
        src: str,
        tgt: str,
        glossary: Optional[Dict[str, str]] = None
    ) -> TranslationResult:
        # Apply glossary terms first
        translated_text = text
        if glossary:
            for term, replacement in glossary.items():
                translated_text = translated_text.replace(term, replacement)

        # Simple reversal for mock behavior
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
        # Placeholder for a real API call to Gemini
        # In a real implementation, you would use the Gemini client library here
        # and incorporate the glossary into the prompt.
        
        # For now, return a placeholder similar to the mock engine
        return TranslationResult(
            original=text,
            translated=f"[GEMINI SIMULATION from {src} to {tgt}] {text}",
            source_language=src,
            target_language=tgt,
            confidence=0.95
        )

# --- Engine Factory ---

def get_engine(name: str, context: dict) -> TranslationEngine:
    """Factory function to get a translation engine instance."""

    if name.lower() == "gemini":
        # Here you could pass API keys or other context from the `context` dict
        return GeminiEngine()
    
    # Default to the mock engine for safety and testing
    return MockEngine()