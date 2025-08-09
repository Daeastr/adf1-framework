import os
import google.generativeai as genai
from .llm_interface import LLMInterface

class GeminiProDelegate(LLMInterface):
    """
    Delegate for interacting with the Google Gemini Pro model.
    [cite_start]Handles authentication, API calls, and error management for Gemini. [cite: 96-97]
    """

    def __init__(self):
        """Initializes the Gemini Pro delegate."""
        print("Initializing GeminiProDelegate...")
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("ERROR: GEMINI_API_KEY environment variable not set.")
            [cite_start]raise ValueError("GEMINI_API_KEY environment variable not set.") [cite: 102]
        
        try:
            [cite_start]genai.configure(api_key=api_key) [cite: 104]
            [cite_start]self.model = genai.GenerativeModel('gemini-pro') [cite: 105]
            print("GeminiProDelegate initialized successfully.")
        except Exception as e:
            print(f"ERROR: Failed to configure Gemini client: {e}")
            raise

    def generate_response(self, prompt: str) -> str:
        """
        [cite_start]Generates a response using the Gemini Pro model. [cite: 107]
        [cite_start]Includes error handling for robust operation. [cite: 108]
        """
        print(f"Sending prompt to Gemini Pro: '{prompt[:50]}...'")
        try:
            [cite_start]response = self.model.generate_content(prompt) [cite: 110]
            print("Received response from Gemini Pro.")
            [cite_start]return response.text [cite: 111]
        except Exception as e:
            [cite_start]print(f"ERROR: Error generating response from Gemini: {e}") [cite: 114]
            [cite_start]return "Error: Could not get a response from the AI model." [cite: 115]
