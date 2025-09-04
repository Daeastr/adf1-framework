from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import json

class Settings(BaseSettings):
    env: str = "dev"
    google_api_key: str
    firebase_project_id: str
    firebase_service_account_json: str  # can be path or raw JSON
    firestore_collection_prefix: str = "prod"
    rate_limit_rps: int = 2
    stt_enabled: bool = False  # if you’ve already added this

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def firebase_credentials(self) -> dict:
        """
        Load Firebase credentials from a file path or JSON string.
        """
        val = self.firebase_service_account_json
        path = Path(val)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return json.loads(val)

settings = Settings()


