import pytest
from core import capability_models as cm

def test_framework_signature_smoke():
    sig = cm.FrameworkSignature(
        supported_tasks=[cm.TaskType.QUESTION_ANSWERING],
        security_features=[cm.SecurityFeature.INPUT_SANITIZATION],
        available_models=[],
        api_endpoints=[],
        base_url="https://example.com",
        documentation_url="https://example.com/docs"
    )
    assert cm.TaskType.QUESTION_ANSWERING in sig.supported_tasks
