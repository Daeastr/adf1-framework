from abc import ABC, abstractmethod

class LLMInterface(ABC):
    """
    Abstract Base Class for LLM delegates.
    [cite_start]Ensures that any implemented delegate has a 'generate_response' method. [cite: 73-74]
    """
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        [cite_start]Generates a response from the LLM based on the given prompt. [cite: 78]
        """
        pass