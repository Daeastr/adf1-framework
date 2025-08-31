# core/orchestrator.py

import argparse
from pathlib import Path
from core.validator import validate_instruction_file, ValidationError
from core.providers.gemini_provider import GeminiProvider  # You'll need this
from core.executor import TaskExecutor  # You'll need this

def load_all_instructions():
    """Load and validate all instruction files"""
    instructions_dir = Path(__file__).parent.parent / "instructions"
    instructions = []
    
    for file_path in instructions_dir.glob("*.json"):
        # Skip the schema definition itself
        if file_path.name == "schema.json":
            continue

        try:
            instruction = validate_instruction_file(file_path)
            print(f"✅ Loaded {file_path.name}: {instruction}")
            instructions.append(instruction)
        except ValidationError as e:
            print(f"❌ {file_path.name} failed validation: {e}")
    
    return instructions

def load_single_instruction(file_path):
    """Load and validate a single instruction file"""
    try:
        instruction = validate_instruction_file(Path(file_path))
        print(f"✅ Loaded {Path(file_path).name}: {instruction}")
        return instruction
    except ValidationError as e:
        print(f"❌ {Path(file_path).name} failed validation: {e}")
        return None

def execute_instruction(instruction):
    """Execute a single instruction using the appropriate provider"""
    if not instruction:
        return None
    
    # Initialize the executor (you'll need to create this)
    executor = TaskExecutor()
    
    try:
        print(f"🚀 Executing {instruction['action']} via {instruction['provider']}")
        result = executor.dispatch(instruction)
        print(f"📊 Result: {result}")
        return result
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='ADF Framework Orchestrator')
    parser.add_argument('instruction_file', nargs='?', 
                       help='Path to instruction JSON file')
    parser.add_argument('--run-single', action='store_true',
                       help='Execute a single instruction file')
    parser.add_argument('--load-all', action='store_true',
                       help='Load and validate all instruction files')
    
    args = parser.parse_args()
    
    if args.run_single and args.instruction_file:
        # Load and execute single instruction
        instruction = load_single_instruction(args.instruction_file)
        if instruction:
            execute_instruction(instruction)
    elif args.load_all or not args.instruction_file:
        # Load all instructions (current behavior)
        load_all_instructions()
    else:
        print("❌ Please specify --run-single with an instruction file, or --load-all")

if __name__ == "__main__":
    main()
