# core/translation_agent.py
import os
from __future__ import annotations
from typing import Optional, Dict

from .agent_base import BaseAgent
# Import the new SafeTranslateClient and the TranslationResult data class
from .translation_engine import SafeTranslateClient, TranslationResult

# --- Placeholder for a real provider SDK ---
# In a real scenario, this would be imported from a library like `google-cloud-translate`
class ProviderClient:
    """A mock SDK class to represent a real translation provider."""
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("ProviderClient requires an API key.")
        self.api_key = api_key
        print(f"Initialized real provider client with API key ending in '...{api_key[-4:]}'")

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        # This is where the actual network call to the provider would happen.
        return f"[LIVE:{source_language}->{target_language}] {text}"

# --- Updated TranslationAgent ---

class TranslationAgent(BaseAgent):
    """
    Agent responsible for coordinating translation requests using a SafeTranslateClient.
    """
    def __init__(
        self,
        name: str = "TranslationAgent",
        **kwargs
    ):
        super().__init__(name, **kwargs)
        # The agent now instantiates the SafeTranslateClient directly.
        # It will try to use the real ProviderClient if an API key is set,
        # otherwise it will fall back to stub mode automatically.
        self.client = SafeTranslateClient(
            provider_cls=ProviderClient,
            api_key=os.getenv("TRANSLATION_API_KEY")
        )

    def run(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        glossary: Optional[Dict[str, str]] = None # Glossary is not used by this simple client
    ) -> TranslationResult:
        """
        Execute a translation request via the configured SafeTranslateClient.
        """
        src_lang = source_language or "auto"
        
        # Call the client, which handles the live call vs. stub fallback
        translated_text = self.client.translate(
            source_lang=src_lang,
            target_lang=target_language,
            text=text
        )

        # The agent's contract is to return a structured TranslationResult object.
        # We construct it here from the client's output.
        is_stub = "[STUB:" in translated_text

        return TranslationResult(
            original=text,
            translated=translated_text,
            source_language=src_lang,
            target_language=target_language,
            confidence=0.95 if not is_stub else 0.50
        )