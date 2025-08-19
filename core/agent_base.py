# core/agent_base.py
class BaseAgent:
    """
    Base class for agents in the automation/delegation framework.
    Provides a common interface for initialization, task execution, and teardown.
    """

    def __init__(self, name: str = "BaseAgent", **kwargs):
        self.name = name
        self.config = kwargs
        self.context = {}

    def setup(self, context: dict | None = None) -> None:
        """
        Optional pre-run setup logic. Override as needed.
        """
        self.context.update(context or {})

    def run(self, *args, **kwargs):
        """
        Main execution entrypoint. Must be overridden by subclasses.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.run() must be implemented.")

    def teardown(self) -> None:
        """
        Optional cleanup logic after run() completes.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"


