import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our framework components
from core.llm_interface import LLMInterface
from core.gemini_delegate import GeminiProDelegate
from core.local_llama_delegate import LocalLlamaDelegate
from core.capability_service import CapabilityService
from core.capability_models import FrameworkSignature
from security.validation import sanitize_input

# Load environment variables from .env file
load_dotenv()

# API Setup
app = FastAPI(
    title="Application Delegation Framework API v2.0",
    description="An AI delegation framework with interchangeable models, security features, and capability discovery for seamless integration.",
    version="2.0.0"
)

# Initialize capability service for discovery
capability_service = CapabilityService()

# Dependency Injection for LLM
def get_llm_delegate() -> LLMInterface:
    # This is the core of interchangeability.
    # Change the return statement to switch AI providers.
    return GeminiProDelegate()
    # return LocalLlamaDelegate()

# API Data Models
class TaskRequest(BaseModel):
    prompt: str

class TaskResponse(BaseModel):
    status: str
    response: str

# API Endpoints
@app.get("/", tags=["Health Check"])
def read_root():
    """Root endpoint for health checks and basic connectivity testing."""
    return {
        "status": "API is running",
        "framework": "Application Delegation Framework",
        "version": "2.0.0",
        "capabilities_endpoint": "/v1/capabilities"
    }

@app.get("/v1/capabilities", response_model=FrameworkSignature, tags=["Capabilities"])
def get_capabilities():
    """Returns the complete capability signature of the framework."""
    return capability_service.get_framework_signature()

@app.post("/v1/delegate-task", response_model=TaskResponse, tags=["AI Delegation"])
def delegate_task(
    request: TaskRequest,
    llm: LLMInterface = Depends(get_llm_delegate)
):
    """Delegates a task to the configured AI model with security validation."""
    try:
        sanitized_prompt = sanitize_input(request.prompt)
        ai_response = llm.generate_response(sanitized_prompt)
        return TaskResponse(status="success", response=ai_response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please check your configuration."
        )