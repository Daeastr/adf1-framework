import time
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import GenerativeModel

# Load environment variables from .env file at the project root
load_dotenv()

# This is kept for a potential auto-picker, but for now, we use a strong default.
def _pick_latest_gemini_model():
    """Returns a powerful default model name."""
    return "gemini-1.5-pro-latest"

class GeminiProvider:
    """
    A provider wrapper for Google's Gemini models that captures telemetry.
    """
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-pro-latest"):
        """
        Initializes the provider, automatically finding the API key from .env
        or environment.
        """
        if api_key is None:
            api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment or .env file")

        genai.configure(api_key=api_key)

        self.model = GenerativeModel(model_name)
        self.api_key = api_key
        print(f"GeminiProvider initialized with model: {model_name}")

    def translate_text(self, text: str, target_lang: str):
        """
        Calls the Gemini API to perform a translation and captures telemetry.
        """
        start = time.time()
        response = self.model.generate_content(f"Translate to {target_lang}: {text}")
        end = time.time()

        class Result: pass
        result = Result()
        result.message = response.text

        usage = getattr(response, "usage_metadata", None)
        result.token_usage = getattr(usage, "total_token_count", None)
        result.latency = end - start
        result.cost_usd = (
            result.token_usage * 0.000002 if result.token_usage is not None else None
        )
        return result
