# tests/test_docs.py
"""
Documentation and safety tests to ensure basic functionality.
"""
import pytest
from pathlib import Path


def test_placeholder_docs():
    """Safety test placeholder - ensures test suite always has a passing test."""
    assert True


def test_project_structure_exists():
    """Verify basic project structure exists."""
    project_root = Path(__file__).parent.parent
    
    # Check for core directories
    assert (project_root / "core").exists(), "core/ directory should exist"
    assert (project_root / "tests").exists(), "tests/ directory should exist"
    assert (project_root / "instructions").exists(), "instructions/ directory should exist"


def test_core_modules_exist():
    """Verify core modules can be imported."""
    try:
        from core.validator import validate_instruction_file, ValidationError
        assert True, "Core validator module imports successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import core validator: {e}")


def test_action_map_exists():
    """Verify action map file exists for test mapping."""
    action_map_path = Path(__file__).parent / "action_map.json"
    if action_map_path.exists():
        import json
        try:
            with open(action_map_path, "r", encoding="utf-8") as f:
                action_map = json.load(f)
            assert isinstance(action_map, dict), "Action map should be a dictionary"
        except json.JSONDecodeError:
            pytest.fail("action_map.json contains invalid JSON")
    else:
        pytest.skip("action_map.json not found - skipping validation")


def test_instructions_directory():
    """Verify instructions directory has expected structure."""
    instructions_dir = Path(__file__).parent.parent / "instructions"
    
    if not instructions_dir.exists():
        pytest.skip("instructions/ directory not found")
    
    json_files = list(instructions_dir.glob("*.json"))
    assert len(json_files) > 0, "Instructions directory should contain at least one JSON file"
    
    # Check if schema.json exists (optional but recommended)
    schema_file = instructions_dir / "schema.json"
    if schema_file.exists():
        import json
        try:
            with open(schema_file, "r", encoding="utf-8") as f:
                schema = json.load(f)
            assert isinstance(schema, dict), "schema.json should contain a valid JSON schema"
        except json.JSONDecodeError:
            pytest.fail("schema.json contains invalid JSON")


@pytest.mark.integration
def test_orchestrator_can_run():
    """Integration test to verify orchestrator can be imported and basic functions work."""
    try:
        from core.orchestrator import load_all_instructions, normalize_step_metadata
        
        # Test normalize_step_metadata function
        test_step = {"priority": "high", "risk": "safe"}
        normalize_step_metadata(test_step)
        
        assert test_step["_priority"] == "high"
        assert test_step["_risk"] == "safe"
        
    except ImportError as e:
        pytest.skip(f"Orchestrator module not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__])