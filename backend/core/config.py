import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/aivideo"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    
    # Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "storage/uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "500000000"))  # 500MB
    
    # Processing
    FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "ffmpeg")
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    
    # API
    API_TITLE: str = "AI Video Studio API"
    API_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"


settings = Settings()
