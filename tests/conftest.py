import pytest

def pytest_configure(config):
    """
    Registers custom markers for the test suite, enabling a multi-dimensional
    testing strategy in the CI pipeline.
    """
    config.addinivalue_line(
        "markers", "stub_provider: stub translation only"
    )
    config.addinivalue_line(
        "markers", "mock_provider: MockTranslateClient tests"
    )
    config.addinivalue_line(
        "markers", "live_provider: real translation provider tests (requires secrets)"
    )