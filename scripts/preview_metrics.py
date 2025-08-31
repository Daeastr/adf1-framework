# scripts/preview_metrics.py
import core.reporting as reporting
import core.executor as executor

# Example step that matches the structure expected by the run_agent_task executor.
# This will call the 'translate_text' action, which in turn will use the
# GeminiProvider to get real telemetry.
test_step = {
    "id": "live-metrics-preview",
    "action": "translate_text",
    "params": {
        "text": "Hello world",
        "target_lang": "fr",
        # Assuming the action can select a provider; otherwise, it uses the default.
        "provider": "gemini" 
    }
}

# In our framework, the orchestrator passes a shared context and the step to the executor.
# For this simple script, we can use an empty context.
print("🚀 Running step through executor to capture live metrics...")
result_step = executor.run_agent_task(test_step, shared_context={})
print("✅ Step execution complete.\n")


# The build_preview_lines function expects a list of step results.
steps_for_reporter = [result_step]

# Build PR-style preview lines from the actual, metric-enriched result.
print("--- Generating PR Comment Preview ---")
lines = reporting.build_preview_lines(steps_for_reporter)
for line in lines:
    print(line)
print("-----------------------------------")