import time
import json
import sys
from pathlib import Path

# ... (imports for executor, action_manager, preview_tools)
from .executor import run_agent_task
from .action_manager import create_context, call_action
from .preview_tools import generate_batch_preview

# This import is critical to ensure that all decorated actions are registered.
import core.actions_translation

def execute_instruction_plan(instruction: dict) -> dict:
    # ... (this function's implementation is correct and complete)
    pass

def run_instruction(instruction: dict):
    # ... (this function's implementation is correct and complete)
    pass

# --- Main Entry Point ---

def main():
    """
    Parses command-line arguments and runs the orchestrator in the specified mode.
    """
    if len(sys.argv) < 2:
        print("Usage: python -m core.orchestrator [run|parse_only] <instruction_file>")
        sys.exit(1)

    mode = sys.argv[1]
    instruction_path = Path(sys.argv[2])

    if not instruction_path.exists():
        print(f"Error: Instruction file not found at {instruction_path}")
        sys.exit(1)

    instruction = json.loads(instruction_path.read_text(encoding="utf-8"))

    if mode == "parse_only":
        print(f"--- Running in PARSE ONLY mode for {instruction_path.name} ---")
        instruction_entry = instruction.copy()

        # --- INDENTATION BLOCK CONFIRMATION ---
        # The 'if' statement is followed by a properly indented block of code,
        # and it has a corresponding 'else' block, resolving any IndentationError.
        segments = instruction.get("segments", [])
        if len(segments) > 1:
            batch_path = generate_batch_preview(instruction["id"], segments)
            instruction_entry["batchPreviewPath"] = str(batch_path)
            print("Generated batch preview at:", batch_path)
        else:
            # This 'else' block ensures the 'if' is properly structured.
            print("No batch preview generated (instruction is not multi-segment).")
        # --- END CONFIRMATION ---
        
        print("\n--- JSON Output for VS Code ---")
        print(json.dumps(instruction_entry, indent=2))

    elif mode == "run":
        print(f"--- Running in FULL EXECUTION mode for {instruction_path.name} ---")
        result = run_instruction(instruction)
        print("\n--- Execution Result ---")
        print(json.dumps(result, indent=2))

    else:
        print(f"Error: Unknown mode '{mode}'. Use 'run' or 'parse_only'.")
        sys.exit(1)


if __name__ == "__main__":
    main()