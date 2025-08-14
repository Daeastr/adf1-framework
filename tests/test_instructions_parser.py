import pytest
from core import instructions_parser as ip
from pathlib import Path
import json

def test_valid_doc(tmp_path):
    doc = {"id": "demo-001", "action": "noop", "params": {}}
    file_path = tmp_path / "demo.json"
    file_path.write_text(json.dumps(doc))
    result = ip.load_and_validate(str(file_path))
    assert result == doc

def test_invalid_doc(tmp_path):
    bad_doc = {"id": "broken"}
    file_path = tmp_path / "bad.json"
    file_path.write_text(json.dumps(bad_doc))
    with pytest.raises(Exception):
        ip.load_and_validate(str(file_path))
