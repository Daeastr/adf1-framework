import json
import jsonschema
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent / "instructions" / "schema.json"

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    SCHEMA = json.load(f)

def load_and_validate(path: str):
    """Load an instruction file and validate against schema.json."""
    with open(path, "r", encoding="utf-8") as f:
        doc = json.load(f)
    jsonschema.validate(instance=doc, schema=SCHEMA)
    return doc
