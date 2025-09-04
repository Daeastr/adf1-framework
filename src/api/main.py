# src/api/main.py
from fastapi import FastAPI, HTTPException, Body, Query, Header, Form, File, UploadFile
from typing import List, Dict

# --- Import Settings and Services ---
# The import path is adjusted to correctly locate the settings instance.
from ..utils.config import settings
# Assuming other services like PairingService are also needed.
from ..services.pairing_service import PairingService

# --- Mock Implementations for Context ---
class MockDBSession: pass
db = MockDBSession()

class MockRateLimiter:
    def allow(self, key: str) -> bool:
        return True
bucket = MockRateLimiter()

def get_user(authorization: str) -> Dict[str, str]:
    return {"uid": "user_abc_123"}

pairing_svc = PairingService(db, settings.firestore_collection_prefix)

# --- FastAPI App and Routes ---
app = FastAPI(
    title="Translation and Pairing Service API",
    description="Manages translation sessions and user pairings.",
)

@app.get("/")
def read_root():
    """A root endpoint to confirm the API is running."""
    return {"status": "ok", "message": "API is running"}

# ... (existing /pair and /accept routes can remain here) ...

# --- NEW /speech ENDPOINT ---
@app.post("/speech")
async def speech(
    conversation_id: str = Form(...),
    sender: str = Form(...),  # e.g. "user1" | "user2"
    audio: UploadFile = File(...),
    authorization: str = Header(None),
):
    """
    Accepts audio, transcribes it, and forwards it as a text message.
    This endpoint is guarded by the 'stt_enabled' feature flag.
    """
    # Optional: verify token, rate limit, etc.
    user = get_user(authorization)
    key = f"speech:{user['uid']}"
    if not bucket.allow(key):
        raise HTTPException(status_code=429, detail="Rate limited")

    # This check ensures the endpoint is disabled until explicitly turned on.
    if not settings.stt_enabled:
        raise HTTPException(status_code=501, detail="Server-side STT disabled")

    # TODO: transcribe audio and forward to add_message
    return {"status": "stub", "conversation_id": conversation_id, "sender": sender}```