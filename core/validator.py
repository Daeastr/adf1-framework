from pathlib import Path
import json
import jsonschema
from jsonschema import validate

SCHEMA_PATH = Path(__file__).parent.parent / "instructions" / "schema.json"

# Load schema once at import time
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    SCHEMA = json.load(f)

class ValidationError(Exception):
    """Raised when an instruction file fails schema validation."""
    pass

def validate_instruction_file(file_path: Path) -> dict:
    """Load a JSON file and validate against the schema.

    Args:
        file_path: Path to the JSON instruction file.

    Returns:
        The loaded JSON as a dict if valid.

    Raises:
        ValidationError: if the file fails schema validation.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    try:
        validate(instance=data, schema=SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        raise ValidationError(f"{file_path} is invalid: {e.message}")
    return data
