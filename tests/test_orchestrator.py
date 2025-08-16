# tests/test_orchestrator.py

from core.orchestrator import run_instruction

def test_sandbox_routing(monkeypatch):
    called = {}

    def fake_run(instruction):
        called["sandbox"] = True
        return {"status": "sandboxed"}

    monkeypatch.setattr("core.sandbox_runner.run_in_sandbox", fake_run)

    result = run_instruction({"id": "demo-003", "action": "noop", "sandbox": True})
    assert called.get("sandbox") is True
    assert result["status"] == "sandboxed"
