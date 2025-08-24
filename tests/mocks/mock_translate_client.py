# tests/mocks/mock_translate_client.py

import logging
from typing import Optional

class MockTranslateClient:
    """
    Stand-in for SafeTranslateClient in CI and unit tests:
      - Deterministic outputs for predictable assertions
      - No external network calls
      - Logs like the real client for cockpit artifact parity
    """

    def __init__(self, api_key: Optional[str] = None, fail: bool = False):
        self.api_key = api_key
        self.fail = fail
        logging.info("[MockTranslateClient] Initialised (fail=%s)", self.fail)

    def translate(self, source_lang: str, target_lang: str, text: str) -> str:
        """
        Simulates a translation call.

        If `fail` is True, it returns a stubbed response.
        Otherwise, it returns a predictable, reversed-text response.
        """
        if self.fail:
            logging.warning("[MockTranslateClient] Simulating provider failure")
            # This mimics the fallback behavior of the SafeTranslateClient
            return f"[STUB:{source_lang}->{target_lang}] {text}"
        
        logging.info("[MockTranslateClient] Simulating provider success")
        # This provides a deterministic, testable transformation
        return f"[MOCK:{source_lang}->{target_lang}] {text[::-1]}"