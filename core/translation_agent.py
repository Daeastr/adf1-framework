# core/translation_agent.py
from .agent_base import BaseAgent
from .translation_engine import translate_text  # adjust if named differently

class TranslationAgent(BaseAgent):
    """Coordinates translation requests inside the delegation framework."""

    def __init__(self, name="TranslationAgent", **kwargs):
        super().__init__(name, **kwargs)

    def can_handle(self, task: str) -> bool:
        return task.strip().lower().startswith("translate")

    def plan(self, task: str, context: dict) -> dict:
        return {"task": task, "context": context}

    def act(self, plan: dict, *_args, **_kwargs) -> str:
        text = plan["task"].replace("translate", "").strip()
        return translate_text(text, target_language="fr")  # adjust as needed
