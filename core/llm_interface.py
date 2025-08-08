from abc import ABC, abstractmethod

class LLMInterface(ABC):
    '''
    Abstract Base Class for LLM delegates.
    Ensures that any implemented delegate has a 'generate_response' method.
    '''
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        '''
        Generates a response from the LLM based on the given prompt.
        '''
        pass

class LocalLlamaDelegate(LLMInterface):
    """
    Delegate for interacting with local LLM models via Ollama or similar.
    Provides offline AI capabilities and data privacy.
    """
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        print(f"Initialized Local Llama Delegate with model: {self.model_name}")
        
    def generate_response(self, prompt: str) -> str:
        """
        Generates response using local Ollama model.
        Requires Ollama to be running locally.
        """
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from local model")
            else:
                return f"Error: Local model unavailable (status: {response.status_code})"
                
        except Exception as e:
            print(f'Error generating response from Local Llama: {e}')
            return 'Error: Could not connect to local AI model. Ensure Ollama is running.'