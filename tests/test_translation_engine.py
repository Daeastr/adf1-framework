# tests/test_translation_engine.py

import os
import pytest
from core.translation_engine import SafeTranslateClient
from tests.mocks.mock_translate_client import MockTranslateClient

@pytest.mark.parametrize("fail", [False, True])
def test_safe_translate_client_with_mock_provider(fail):
    """
    Tests that the SafeTranslateClient correctly uses a mock provider
    and handles both success and failure modes.
    """
    # We use a lambda function to inject the 'fail' parameter into the
    # mock's constructor when the SafeTranslateClient initializes it.
    client = SafeTranslateClient(
        provider_cls=lambda api_key: MockTranslateClient(api_key=api_key, fail=fail),
        api_key="dummy-key-for-testing"
    )

    output = client.translate(source_lang="en", target_lang="fr", text="hello")

    if fail:
        # When the mock provider fails, we expect the SafeTranslateClient's
        # internal fallback stub to be triggered.
        assert output.startswith("[STUB:en->fr]")
        assert output.endswith(" hello")
    else:
        # When the mock provider succeeds, we expect its deterministic
        # (reversed text) output.
        assert output.startswith("[MOCK:en->fr]")
        assert output.endswith(" olleh")

def test_safe_translate_client_in_stub_mode_no_key():
    """
    Tests that SafeTranslateClient falls back to stub mode when no API key is provided,
    without even attempting to initialize the provider.
    """
    client = SafeTranslateClient(
        provider_cls=MockTranslateClient,
        api_key=None  # No API key
    )
    output = client.translate(source_lang="en", target_lang="de", text="world")
    assert output.startswith("[STUB:en->de]")
    assert output.endswith(" world")