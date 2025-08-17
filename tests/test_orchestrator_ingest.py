import json
from pathlib import Path
from core import orchestrator
import pytest


def test_load_valid_instructions_reads_valid(tmp_path, monkeypatch):
    valid_doc = {"id": "demo-002", "action": "noop", "params": {}}
    (tmp_path / "demo.json").write_text(json.dumps(valid_doc), encoding="utf-8")

    monkeypatch.setattr(orchestrator, "INSTR_DIR", tmp_path)

    result = orchestrator.load_valid_instructions()
    assert result == [valid_doc]


def test_load_valid_instructions_skips_invalid(tmp_path, monkeypatch):
    # invalid doc (missing required keys)
    invalid_doc = {"id": "oops"}
    (tmp_path / "bad.json").write_text(json.dumps(invalid_doc), encoding="utf-8")

    monkeypatch.setattr(orchestrator, "INSTR_DIR", tmp_path)

    result = orchestrator.load_valid_instructions()
    # Expect empty list, invalid JSON/docs are skipped not raised
    assert result == []
