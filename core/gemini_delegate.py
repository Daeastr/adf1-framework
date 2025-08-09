import os
import google.generativeai as genai
from .llm_interface import LLMInterface

class GeminiProDelegate(LLMInterface):
    """Delegate for interacting with the Google Gemini Pro model."""
    
    def __init__(self):
        """Initializes the Gemini Pro delegate."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_response(self, prompt: str) -> str:
        """Generates a response using the Gemini Pro model."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # In a real app, you'd use your structured logger here
            print(f"Error generating response from Gemini: {e}")
            return "Error: Could not get a response from the AI model."