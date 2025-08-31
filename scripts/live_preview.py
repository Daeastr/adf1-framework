import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core import executor, reporting
"""
Run a sample step through your executor and print PR-style preview lines.
Works with your core/executor.py + core/reporting.py setup.
"""

# Example step list — adjust to hit your real provider
steps = [
    {
        "name": "translate_text",
        "input": "Hello world",
        "target_lang": "fr"
    }
]

# Run all steps (this will also write a log if your executor has the log-writer patch)
executed_steps = executor.run_all(steps)

# Build PR-style preview lines
lines = reporting.build_preview_lines(executed_steps)

# Print them exactly as they'd appear in a PR comment
for line in lines:
    print(line)
