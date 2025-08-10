import pytest
from unittest.mock import patch, MagicMock

# Add this at the top of your test file
@pytest.fixture(autouse=True)
def mock_gemini_delegate():
    with patch('apis.main.get_llm_delegate') as mock_get_delegate:
        mock_delegate = MagicMock()
        mock_delegate.generate_response.return_value = "Mocked response"
        mock_get_delegate.return_value = mock_delegate
        yield mock_delegate
