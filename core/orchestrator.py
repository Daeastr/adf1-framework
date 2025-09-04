# core/orchestrator.py
from typing import Any, Dict

# Ensure actions registry exists
_actions: dict[str, callable] = {}

def register_action(name: str):
    """Decorator to register an action by name."""
    def decorator(func):
        _actions[name] = func
        return func
    return decorator

def call_action(name: str, *args, **kwargs) -> Any:
    """Look up and execute a registered action by name."""
    if name not in _actions:
        raise ValueError(f"Action '{name}' not registered.")
    return _actions[name](*args, **kwargs)

def create_context(**kwargs) -> Dict[str, Any]:
    """Factory for an execution context passed into actions."""
    context = {
        "user": kwargs.get("user", "system"),
        "meta": kwargs.get("meta", {}),
        # add any other default keys your actions expect
    }
    return context

# Force-load actions so they self-register
from core import actions_translation  # noqa: E402