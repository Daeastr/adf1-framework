# In core/local_llama_delegate.py
import requests
from .llm_interface import LLMInterface

class LocalLlamaDelegate(LLMInterface):
    [cite_start]"""Delegate for interacting with a local LLM via an API endpoint (e.g., Ollama) [cite: 647-648]."""
    def __init__(self, api_url: str = "http://localhost:11434/api/generate", model_name: str = "llama3"):
        self.api_url = api_url
        self.model_name = model_name
        [cite_start]print(f"Initialized Local Llama Delegate with model: {self.model_name}") [cite: 651]

    def generate_response(self, prompt: str) -> str:
        [cite_start]"""Generates a response from the local LLM[cite: 652]."""
        [cite_start]print(f"Sending prompt to Local Llama: '{prompt}'") [cite: 654]
        
        # This is where you would make the actual API call to a local model server.
        # This example is for Ollama's API format.
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False 
            }
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status() # Raise an exception for bad status codes
            
            # Assuming the local API returns a JSON with a "response" key
            return response.json().get("response", "Error: No response field in local model reply.")

        except requests.exceptions.RequestException as e:
            print(f"Error calling local model: {e}")
            return "Error: Could not get a response from the local AI model."
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "Error: An unexpected error occurred with the local model."

