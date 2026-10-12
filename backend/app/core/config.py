import os
import secrets
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = (BASE_DIR.parent / "data").resolve()
STORAGE_DIR = (BASE_DIR.parent / "storage").resolve()

# Ensure runtime directories exist with absolute paths
DATA_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_file=".env")

    APP_NAME: str = "SmartInvoice AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Security: Secret API Key required for all data and document endpoints
    # Can be configured in .env; defaults to a predictable local development key
    API_KEY: str = os.getenv("SMARTINVOICE_API_KEY", "smartinvoice-secret-key-2026")
    
    # Database: Absolute path to local SQLite
    DATABASE_PATH: Path = DATA_DIR / "smartinvoice.db"
    
    # Cloud Supabase Database (Optional / Cloud Sync)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://nulztcolczlmmnvecals.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "sb_publishable_V5qKKlaNUiWsqI6RBVWHyw_EjnaObw6")

    # Storage: Absolute path
    STORAGE_PATH: Path = STORAGE_DIR
    
    # OCR Settings
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "tesseract")
    
    # Max file upload size in bytes (10 MB)
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024

    # CORS: Allow trusted origins (Local development, mobile local network, Vercel, Netlify, Render, Railway, Fly.io)
    CORS_ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ] + [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    CORS_ALLOW_ALL_ORIGINS_REGEX: str = os.getenv(
        "CORS_ALLOW_ALL_ORIGINS_REGEX",
        r"^https:\/\/.*(\.vercel\.app|\.netlify\.app|\.pages\.dev|\.onrender\.com|\.railway\.app|\.fly\.dev|\.loca\.lt|\.trycloudflare\.com)$|^http:\/\/192\.168\.\d+\.\d+(:\d+)?$|^http:\/\/10\.\d+\.\d+\.\d+(:\d+)?$",
    )



settings = Settings()
