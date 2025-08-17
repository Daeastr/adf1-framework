import json
from pathlib import Path

import core.orchestrator as orch


def test_load_valid_instructions_skips_malformed_and_schema(tmp_path, monkeypatch):
    # Prepare temporary instruction files
    valid = tmp_path / "valid.json"
    valid.write_text(json.dumps({"id": "step-valid", "action": "do_work", "params": {}}), encoding="utf-8")

    malformed = tmp_path / "malformed.json"
    # write broken JSON
    malformed.write_text('{"id": "step-bad", "action": "oops",', encoding="utf-8")

    partial = tmp_path / "partial.json"
    # missing 'params' key
    partial.write_text(json.dumps({"id": "step-partial", "action": "maybe"}), encoding="utf-8")

    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps({"$schema": "http://example"}), encoding="utf-8")

    # Point the loader at our temp folder
    monkeypatch.setattr(orch, "INSTR_DIR", tmp_path)

    results = orch.load_valid_instructions()

    # Only the fully valid instruction should be returned
    assert isinstance(results, list)
    ids = [r.get("id") for r in results]
    assert ids == ["step-valid"]
