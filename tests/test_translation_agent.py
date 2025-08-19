# tests/test_translation_agent.py
import pytest
from core.agents import BaseAgent
from core.translation_agent import TranslationAgent

def test_translation_agent_is_base_agent():
    """
    Tests that TranslationAgent is a subclass of BaseAgent.
    """
    agent = TranslationAgent()
    assert isinstance(agent, BaseAgent)

def test_translation_agent_can_handle_simple_task():
    """
    Tests the can_handle method with a direct translation request.
    """
    agent = TranslationAgent()
    task = "translate this text to french"
    assert agent.can_handle(task) is True

def test_translation_agent_ignores_unrelated_task():
    """
    Tests that the agent correctly ignores tasks it cannot handle.
    """
    agent = TranslationAgent()
    task = "summarize this document"
    assert agent.can_handle(task) is False

def test_translation_agent_plan_creation():
    """
    Tests that the agent creates its expected three-step plan.
    """
    agent = TranslationAgent()
    task = "translate 'hello' to spanish"
    plan = agent.plan(task, {})
    assert "steps" in plan
    assert len(plan["steps"]) == 3
    assert plan["steps"][1] == "call translation_engine"

# Add more tests for the 'act' method as needed
# For example, you might mock the 'translate_text' function to test 'act' logic
# without making a real LLM call.