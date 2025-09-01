import time
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import GenerativeModel

# Load environment variables from a .env file at the project root
load_dotenv()

def _pick_latest_gemini_model():
    """
    Returns the newest Gemini model that supports generateContent.
    Falls back to a powerful default if the API call fails or no models are found.
    """
    try:
        print("[GeminiProvider] Querying for the latest available models...")
        # Filter models to find the latest compatible Gemini model
        models = [
            m.name.split("/")[-1]
            for m in genai.list_models()
            if "gemini" in m.name and "generateContent" in m.supported_generation_methods
        ]
        if models:
            models.sort() # Sort alphabetically/numerically to find the latest
            latest_model = models[-1]
            print(f"[GeminiProvider] Auto-selected model: {latest_model}")
            return latest_model
    except Exception as e:
        print(f"[GeminiProvider] Could not auto-pick model due to an API error: {e}. Falling back.")
    # A safe, powerful default
    print("[GeminiProvider] Falling back to default model: gemini-1.5-pro-latest")
    return "gemini-1.5-pro-latest"

class GeminiProvider:
    """
    A provider wrapper for Google's Gemini models that captures and returns
    detailed telemetry (tokens, latency, cost) for each API call.
    """
    def __init__(self, api_key: str = None, model_name: str = None):
        """
        Initializes the provider, automatically finding the API key from .env
        or environment, and selecting the latest model if not specified.
        """
        if api_key is None:
            api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment or .env file")

        genai.configure(api_key=api_key)

        if not model_name:
            model_name = _pick_latest_gemini_model()

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