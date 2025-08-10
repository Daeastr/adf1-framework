from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum

class TaskType(str, Enum):
    TEXT_GENERATION = 'text_generation'
    YoutubeING = 'Youtubeing'
    CREATIVE_WRITING = 'creative_writing'
    CODE_ASSISTANCE = 'code_assistance'
    ANALYSIS = 'analysis'
    SUMMARIZATION = 'summarization'

class SecurityFeature(str, Enum):
    PROMPT_INJECTION_PROTECTION = 'prompt_injection_protection'
    INPUT_SANITIZATION = 'input_sanitization'
    RATE_LIMITING = 'rate_limiting'
    CONTENT_FILTERING = 'content_filtering'

class ModelProvider(str, Enum):
    GOOGLE_GEMINI = 'google_gemini'
    OPENAI = 'openai'
    ANTHROPIC_CLAUDE = 'anthropic_claude'
    LOCAL_LLAMA = 'local_llama'
    OLLAMA = 'ollama'

class APICapability(BaseModel):
    endpoint: str
    method: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    example_request: Dict[str, Any]
    example_response: Dict[str, Any]

class ModelCapability(BaseModel):
    provider: ModelProvider
    model_name: str
    is_active: bool
    max_tokens: Optional[int] = None
    supports_streaming: bool = False
    cost_per_request: Optional[float] = None
    response_time_avg_ms: Optional[int] = None

class FrameworkSignature(BaseModel):
    name: str = 'Application Delegation Framework'
    version: str = '2.0.0'
    description: str = 'Interchangeable AI delegation framework with security features and capability discovery'
    supported_tasks: List[TaskType]
    security_features: List[SecurityFeature]
    available_models: List[ModelCapability]
    api_endpoints: List[APICapability]
    base_url: str
    documentation_url: str
    max_concurrent_requests: int = 100
    supports_batch_processing: bool = False
    supports_async: bool = True
    authentication_required: bool = False
    rate_limits: Dict[str, int] = {'requests_per_minute': 60}
    health_check_endpoint: str = '/health'
    metrics_endpoint: Optional[str] = None
    deployment_type: str = 'api_service'
    scaling_type: str = 'horizontal'
    resource_requirements: Dict[str, str] = {
        'cpu': '0.5 cores',
        'memory': '1GB',
        'storage': 'minimal'
    }