from pathlib import Path
from json import JSONDecodeError
from core.validator import validate_instruction_file, ValidationError

for fp in Path("instructions").glob("*.json"):
    if fp.name == "schema.json":
        continue
    try:
        validate_instruction_file(fp)
    except JSONDecodeError as e:
        print(f"[SYNTAX ERROR] {fp}: {e}")
    except ValidationError as e:
        print(f"[SCHEMA ERROR] {fp}: {e}")
    else:
        print(f"[OK] {fp.name}")
