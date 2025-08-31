import time
from core.providers.gemini import GeminiProvider

gemini = GeminiProvider(api_key="YOUR_KEY")

def run_step(step):
    step["start_time"] = time.time()
    step["metrics"] = {}
    try:
        if step["name"] == "translate_text":
            result = gemini.translate_text(step["input"], step["target_lang"])
        else:
            # Replace with your branch's real action runner or a stub
            result = _execute_action(step)

        # Capture provider metrics from the result object
        if hasattr(result, "token_usage"):
            step["metrics"]["tokens"] = result.token_usage
        if hasattr(result, "latency"):
            step["metrics"]["latency"] = result.latency
        if hasattr(result, "cost_usd"):
            step["metrics"]["cost_usd"] = result.cost_usd

        step["status"] = "✅"
        step["message"] = getattr(result, "message", "")
    except Exception as e:
        step["status"] = "❌"
        step["message"] = str(e)
    finally:
        step["end_time"] = time.time()
    return step
