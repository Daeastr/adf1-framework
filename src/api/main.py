# src/api/main.py
from fastapi import FastAPI, HTTPException, Body, Query, Header, Form, File, UploadFile
from typing import List, Dict

# --- Import Settings and Services ---
from ..services.pairing_service import PairingService
from ..utils.config import settings # Import the settings instance

# --- Mock Implementations for Context ---
class MockDBSession: pass
db = MockDBSession()

class MockRateLimiter:
    def allow(self, key: str) -> bool:
        print(f"Rate limit check for: {key}")
        return True
bucket = MockRateLimiter()

def get_user(authorization: str) -> Dict[str, str]:
    print(f"Auth check for header: {authorization}")
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

# ... (existing /pair and /accept routes) ...
@app.post("/pair")
async def create_pair(conversation_id: str = Query(...), authorization: str = Header(None)):
    # ... implementation
    pass

@app.post("/accept")
async def accept_pair(code: str = Query(...), authorization: str = Header(None)):
    # ... implementation
    pass


# --- PATCH APPLIED HERE: NEW /speech ENDPOINT ---
@app.post("/speech")
async def speech(
    conversation_id: str = Form(...),
    sender: str = Form(...),  # e.g., "user1" or "user2"
    audio: UploadFile = File(...),
    authorization: str = Header(None),
):
    """
    Accepts audio, transcribes it, and forwards it as a text message.
    This endpoint is guarded by the 'stt_enabled' feature flag.
    """
    user = get_user(authorization)
    key = f"speech:{user['uid']}"
    if not bucket.allow(key):
        raise HTTPException(status_code=429, detail="Rate limited")

    # This check ensures the endpoint is disabled until explicitly turned on.
    if not settings.stt_enabled:
        raise HTTPException(status_code=501, detail="Server-side STT disabled")

    # 🔜 When enabled: transcribe audio here, then forward text into add_message
    return {"status": "ok", "note": "STT disabled — endpoint scaffold only"}