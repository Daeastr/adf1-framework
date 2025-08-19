# core/translation_agent.py
from .agent_base import BaseAgent
from .translation_engine import TranslationEngine  # adjust if actual class/function name differs

class TranslationAgent(BaseAgent):
    """
    Agent responsible for coordinating translation requests
    within the delegation framework.
    """

    def __init__(self, name="TranslationAgent", engine=None, **kwargs):
        super().__init__(name, **kwargs)
        self.engine = engine or TranslationEngine()

    def run(self, text: str, target_language: str) -> str:
        """
        Execute a translation request.
        """
        # You can expand with logging, rollback hooks, etc.
        return self.engine.translate(text, target_language)

