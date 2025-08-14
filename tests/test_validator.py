import pytest
from core import validator

def test_validator_accepts_minimal_doc(tmp_path):
    # Create a minimal, valid file
    doc_file = tmp_path / "demo.json"
    doc_file.write_text('{"id": "demo-000", "action": "noop", "params": {}}')
    result = validator.validate_instruction_file(str(doc_file))
    assert result is True

def test_validator_rejects_invalid_doc(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{}")  # missing required fields
    with pytest.raises(Exception):
        validator.validate_instruction_file(str(bad_file))
def test_validator_accepts_minimal_doc(tmp_path):
    # Create a minimal, valid file
    doc_file = tmp_path / "demo.json"
    doc_file.write_text('{"id": "demo-000", "action": "noop", "params": {}}')
    result = validator.validate_instruction_file(str(doc_file))
    assert result  # any truthy return means it validated successfully
