"""
Integration test for the Translation App action handlers.
Covers the full step chain: init → propose → interject → end.
Ensures each step runs in safe mode, returns expected keys,
and leaves a per-step log file artifact.
"""

import pytest

from core.actions_translation import (
    translation_init,
    translation_propose,
    translation_interject,
    translation_end,
)

@pytest.mark.translation
@pytest.mark.actions
def test_translation_full_cycle(tmp_path):
    """
    Run the full translation workflow in safe_mode and verify:
      1. Each handler returns the expected status.
      2. A 'record' is present in init/end steps.
      3. Each step result includes a '_log_file' key.
    """
    # Step counter & params
    step_counter = 1
    init_params = {
        "source_lang": "en",
        "target_lang": "fr",
        "text": "Hello world",
    }

    # STEP 1 — init
    init_result = translation_init(f"step_{step_counter}", init_params, safe_mode=True)
    assert init_result["status"] in ("initialized", "initialized_safe_mode")
    assert "record" in init_result
    assert "_log_file" in init_result
    step_counter += 1

    # STEP 2 — propose
    propose_params = {
        "session_id": init_result["record"]["session_id"],
        "proposal": "Bonjour le monde",
    }
    propose_result = translation_propose(f"step_{step_counter}", propose_params, safe_mode=True)
    assert propose_result["status"] in ("proposal_created", "proposal_created_safe_mode")
    assert "_log_file" in propose_result
    step_counter += 1

    # STEP 3 — interject
    interject_params = {
        "session_id": init_result["record"]["session_id"],
        "comment": "Consider formal tone",
    }
    interject_result = translation_interject(f"step_{step_counter}", interject_params, safe_mode=True)
    assert interject_result["status"] in ("interjection_added", "interjection_added_safe_mode")
    assert "_log_file" in interject_result
    step_counter += 1

    # STEP 4 — end
    end_params = {
        "session_id": init_result["record"]["session_id"],
    }
    end_result = translation_end(f"step_{step_counter}", end_params, safe_mode=True)
    assert end_result["status"] in ("closed", "closed_safe_mode")
    assert "record" in end_result
    assert "_log_file" in end_result

    # Final cross-check: every step leaves a log file
    for result in [init_result, propose_result, interject_result, end_result]:
        assert "_log_file" in result, f"Missing _log_file in {result.get('status')}"

