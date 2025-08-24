# tests/conftest.py
import pytest

def pytest_configure(config):
    """
    Registers custom markers for the test suite. This allows us to select
    tests based on their interaction with external services.
    """
    config.addinivalue_line(
        "markers", "stub_provider: tests that rely on the offline, fallback stub translation only"
    )
    config.addinivalue_line(
        "markers", "mock_provider: tests that use the MockTranslateClient to simulate a provider"
    )
    config.addinivalue_line(
        "markers", "live_provider: tests that make real network calls to the translation provider (requires API key)"
    )