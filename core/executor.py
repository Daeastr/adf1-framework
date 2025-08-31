# core/executor.py
import time

def run_step(step):
    step["start_time"] = time.time()
    step["metrics"] = {}  # NEW: provider telemetry

    try:
        result = _execute_action(step)  # your existing action runner

        # Capture provider stats if present
        if hasattr(result, "token_usage"):
            step["metrics"]["tokens"] = result.token_usage
        if hasattr(result, "latency"):
            step["metrics"]["latency"] = result.latency
        if hasattr(result, "cost_usd"):
            step["metrics"]["cost_usd"] = result.cost_usd

        step["status"] = "✅"
        step["message"] = result.message

    except Exception as e:
        step["status"] = "❌"
        step["message"] = str(e)

    finally:
        step["end_time"] = time.time()

    return step
