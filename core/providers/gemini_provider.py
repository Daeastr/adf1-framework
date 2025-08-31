import os
import time
import google.generativeai as genai

class GeminiProvider:
    def __init__(self, model: str = "gemini-pro"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set in environment")
        genai.configure(api_key=api_key)
        self.model = model

    def translate_text(self, text: str, target_lang: str):
        start_time = time.time()

        prompt = f"Translate the following text to {target_lang}:\n\n{text}"
        response = genai.GenerativeModel(self.model).generate_content(prompt)

        end_time = time.time()
        elapsed = end_time - start_time

        # Usage metadata may vary depending on SDK version
        usage = getattr(response, "usage_metadata", None)
        token_usage = getattr(usage, "total_token_count", None)

        # Simple cost calculation (adjust rates to your pricing)
        cost_usd = None
        if token_usage is not None:
            # Example: $0.000002 per token
            cost_usd = token_usage * 0.000002

        return {
            "translated_text": response.text,
            "token_usage": token_usage,
            "latency": elapsed,
            "cost_usd": cost_usd
        }
