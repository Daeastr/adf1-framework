# src/core/providers/gemini.py
import time
from google.generativeai import GenerativeModel

class GeminiProvider:
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        self.model = GenerativeModel(model_name)
        self.api_key = api_key

    def translate_text(self, text: str, target_lang: str):
        start = time.time()
        response = self.model.generate_content(
            f"Translate to {target_lang}: {text}"
        )
        end = time.time()

        class Result: pass
        result = Result()
        result.message = response.text

        usage = getattr(response, "usage_metadata", None)
        result.token_usage = getattr(usage, "total_token_count", None)
        result.latency = end - start
        result.cost_usd = (
            result.token_usage * 0.000002 if result.token_usage else None
        )
        return result
