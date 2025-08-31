# core/executor.py
import time
import google.generativeai as genai

# Configure Gemini (you'll need to set your API key)
# genai.configure(api_key="your-api-key-here")  # Uncomment and add your key

class ExecutionResult:
    """Simple result wrapper to hold response data and metrics"""
    def __init__(self, message, token_usage=None, latency=None, cost_usd=None):
        self.message = message
        self.token_usage = token_usage
        self.latency = latency
        self.cost_usd = cost_usd

def _execute_action(step):
    """Execute the actual action based on step configuration"""
    provider = step["provider"]
    action = step["action"] 
    params = step["params"]
    model = step["model"]
    
    if provider == "gemini":
        return _execute_gemini_action(action, params, model)
    else:
        raise ValueError(f"Unknown provider: {provider}")

def _execute_gemini_action(action, params, model):
    """Execute Gemini-specific actions"""
    start_time = time.time()
    
    if action == "translate_text":
        # Initialize Gemini model
        gemini_model = genai.GenerativeModel(model)
        
        # Create translation prompt
        text = params["text"]
        target_lang = params["target_lang"]
        prompt = f"Translate the following text to {target_lang}: {text}"
        
        # Make API call
        response = gemini_model.generate_content(prompt)
        
        # Calculate latency
        latency = time.time() - start_time
        
        # Return result with metrics (you can enhance this with actual token counting)
        return ExecutionResult(
            message=response.text,
            latency=latency,
            token_usage={"input": len(prompt), "output": len(response.text)},  # Rough estimate
            cost_usd=0.001  # Rough estimate - you'd calculate this based on actual pricing
        )
    else:
        raise ValueError(f"Unknown Gemini action: {action}")

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