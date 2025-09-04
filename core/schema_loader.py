# core/schema_loader.py

import json
from pathlib import Path

# Adjust if your schema file lives somewhere else
SCHEMA_PATH = Path(__file__).parent / "instruction_schema.json"

def load_schema():
    """
    Load and return the JSON schema for instructions.
    Raises FileNotFoundError if the schema file is missing.
    Raises json.JSONDecodeError if the schema file is invalid JSON.
    """
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

