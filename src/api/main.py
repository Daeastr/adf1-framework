# src/api/main.py
from fastapi import FastAPI, HTTPException, Body, Query, Header
from typing import List, Dict

# --- Mock Implementations for Context ---
# Assume 'db' and 'settings' are initialized here for the application context
class MockDBSession: pass
class MockSettings:
    firestore_collection_prefix = "dev"
db = MockDBSession()
settings = MockSettings()

# Mock for the rate-limiting bucket
class MockRateLimiter:
    def allow(self, key: str) -> bool:
        print(f"Rate limit check for: {key}")
        return True
bucket = MockRateLimiter()

# Mock for the user authentication function
def get_user(authorization: str) -> Dict[str, str]:
    print(f"Auth check for header: {authorization}")
    # In a real app, this would decode a JWT or token
    return {"uid": "user_abc_123"}

# --- Service Instantiation ---
from ..services.pairing_service import PairingService
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

# Placeholder for an existing /message route if it exists.

# --- PATCH APPLIED HERE: NEW ROUTES APPENDED ---

@app.post("/pair")
async def create_pair(conversation_id: str = Query(...), authorization: str = Header(None)):
    """Create a PIN invite for user1→user2 pairing."""
    user = get_user(authorization)
    key = f"pair:{user['uid']}"
    if not bucket.allow(key):
        raise HTTPException(status_code=429, detail="Rate limited")
    
    # In a real async app, this would likely be awaited
    invite = pairing_svc.create_invite(conversation_id, user["uid"])
    return invite  # {invite_id, code}

@app.post("/accept")
async def accept_pair(code: str = Query(...), authorization: str = Header(None)):
    """Accept a PIN invite and join conversation as user2."""
    user = get_user(authorization)
    key = f"accept:{user['uid']}"
    if not bucket.allow(key):
        raise HTTPException(status_code=429, detail="Rate limited")
    
    # In a real async app, this would likely be awaited
    result = pairing_svc.accept(code, user["uid"])
    if "error" in result:
         raise HTTPException(status_code=400, detail=result["error"])
    return result  # {conversation_id}