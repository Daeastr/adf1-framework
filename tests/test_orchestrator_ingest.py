import json
from pathlib import Path
from core import orchestrator
import pytest

def test_ingest_reads_and_validates(tmp_path, monkeypatch):
    # valid doc
    valid_doc = {"id": "demo-002", "action": "noop", "params": {}}
    (tmp_path / "demo.json").write_text(json.dumps(valid_doc))

    # patch orchestrator's path to point to our tmp dir
    monkeypatch.setattr(orchestrator, "Path", lambda *_: Path(tmp_path))

    result = orchestrator.load_all_instructions()
    assert result == [valid_doc]

def test_ingest_fails_on_invalid(tmp_path, monkeypatch):
    invalid_doc = {"id": "oops"}
    (tmp_path / "bad.json").write_text(json.dumps(invalid_doc))

    monkeypatch.setattr(orchestrator, "Path", lambda *_: Path(tmp_path))

    with pytest.raises(Exception):
        orchestrator.load_all_instructions()
import json
from core import orchestrator
import pytest

def test_ingest_reads_and_validates(tmp_path, monkeypatch):
    # valid doc
    valid_doc = {"id": "demo-002", "action": "noop", "params": {}}
    (tmp_path / "demo.json").write_text(json.dumps(valid_doc))

    # 👇 Patch the orchestrator to read from our tmp dir
    monkeypatch.setattr(orchestrator, "INSTRUCTIONS_DIR", tmp_path)

    result = orchestrator.load_all_instructions()
    assert result == [valid_doc]

def test_ingest_fails_on_invalid(tmp_path, monkeypatch):
    # invalid doc (missing required keys)
    invalid_doc = {"id": "oops"}
    (tmp_path / "bad.json").write_text(json.dumps(invalid_doc))

    # 👇 Patch the orchestrator to read from our tmp dir
    monkeypatch.setattr(orchestrator, "INSTRUCTIONS_DIR", tmp_path)

    with pytest.raises(Exception):
        orchestrator.load_all_instructions()
