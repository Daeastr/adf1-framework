# core/translation_agent.py
from __future__ import annotations
from typing import Optional, Dict

# No import needed for TranslationEngine from this file's perspective.
# Any other file can now safely import it from its canonical location.
from core.agent_base import BaseAgent
from core.translation_engine import TranslationEngine, get_engine, TranslationResult


class TranslationAgent(BaseAgent):
    """
    Agent responsible for coordinating translation requests
    within the delegation framework.
    """

    def __init__(
        self,
        name: str = "TranslationAgent",
        engine: Optional[TranslationEngine] = None,
        **kwargs
    ):
        super().__init__(name, **kwargs)
        # Fallback to default/mock engine if none provided
        self.engine = engine or get_engine("mock", context={})

    def run(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        glossary: Optional[Dict[str, str]] = None
    ) -> TranslationResult:
        """
        Execute a translation request via the configured engine.
        """
        return self.engine.translate(
            text=text,
            src=source_language or "auto",
            tgt=target_language,
            glossary=glossary
        )