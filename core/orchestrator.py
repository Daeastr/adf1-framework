# core/orchestrator.py

for file_path in instructions_dir.glob("*.json"):
    # ⬇ Skip the schema definition itself
    if file_path.name == "schema.json":
        continue
    try:
        instruction = validate_instruction_file(file_path)
        print(f"✅ Loaded {file_path.name}: {instruction}")
    except ValidationError as e:
        print(f"❌ {file_path.name} failed validation: {e}")


