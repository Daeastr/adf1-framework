from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Manages all application settings, loading them from environment variables
    and .env files. This provides a single, type-safe source of truth for
    all configuration.
    """
    # Core application settings
    env: str = "dev"
    firestore_collection_prefix: str = "prod"

    # API Keys and Service Credentials
    google_api_key: str
    firebase_project_id: str
    firebase_service_account_json: str
    
    # Feature-specific settings
    rate_limit_rps: int = 2
    stt_enabled: bool = False  # NEW: toggle for server-side speech-to-text

    class Config:
        # Pydantic will automatically look for and load variables from a .env file.
        env_file = ".env"

# Create a single, importable instance of the settings for the whole app to use.
settings = Settings()