# apis/main.py

import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our framework components
from core.llm_interface import LLMInterface
from core.gemini_delegate import GeminiProDelegate
from core.local_llama_delegate import LocalLlamaDelegate
from security.validation import sanitize_input

# Load environment variables from .env file
load_dotenv()

# --- API Setup ---
app = FastAPI(
    title="Application Delegation Framework API",
    description="An API to interact with interchangeable AI delegates securely."
)

# --- Dependency Injection for LLM ---
def get_llm_delegate() -> LLMInterface:
    """
    This function is the heart of interchangeability.
    Change the returned delegate to switch the LLM for the entire application.
    """
    # To use Gemini Pro:
    return GeminiProDelegate()
    
    # To use a local Llama model via Ollama:
    # return LocalLlamaDelegate()

# --- API Data Models ---
class TaskRequest(BaseModel):
    prompt: str

class TaskResponse(BaseModel):
    status: str
    response: str

# --- API Endpoints ---
@app.get("/", tags=["Health Check"])
def read_root():
    """Root endpoint for health checks."""
    return {"status": "API is running"}

@app.post("/v1/delegate-task", response_model=TaskResponse, tags=["Delegation"])
def delegate_task(
    request: TaskRequest, 
    llm: LLMInterface = Depends(get_llm_delegate)
):
    """
    Receives a prompt, sanitizes it, and delegates it to the configured LLM.
    """
    try:
        # 1. Security First: Sanitize the input
        sanitized_prompt = sanitize_input(request.prompt)

        # 2. Delegate to the configured LLM
        ai_response = llm.generate_response(sanitized_prompt)

        # 3. Return the response
        return {"status": "success", "response": ai_response}

    except ValueError as e:
        # Catches the prompt injection error from our validator
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Generic error handler for other issues
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")