# core/translation_agent.py
from __future__ import annotations
from typing import Optional, Dict
from .agent_base import BaseAgent
from .translation_engine import TranslationEngine, get_engine, TranslationResult

class TranslationAgent(Base.Agent):
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

        :param text: The text to translate.
        :param target_language: Target language code (e.g., 'es').
        :param source_language: Optional source language code; if None, engine may auto-detect.
        :param glossary: Optional term replacements for domain-specific translation.
        :return: TranslationResult containing original, translated, languages, confidence.
        """
        # Here you can expand with logging, rollback hooks, or artifact writes
        return self.engine.translate(
            text=text,
            src=source_language or "auto",
            tgt=target_language,
            glossary=glossary
        )