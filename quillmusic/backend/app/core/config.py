"""
QuillMusic Backend Configuration
"""
from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # App Info
    APP_NAME: str = "QuillMusic"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # API
    API_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str = "sqlite:///./quillmusic.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5000",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.replit.dev",
        "https://*.repl.co",
    ]

    # Song Blueprint Engine Configuration
    SONG_ENGINE_MODE: Literal["fake", "llm"] = "fake"

    # LLM Configuration (for song blueprint generation)
    LLM_API_BASE: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL_NAME: str = "gpt-4.1-mini"
    LLM_PROVIDER: str = "openai-compatible"

    # Audio Provider Configuration (for instrumental rendering)
    AUDIO_PROVIDER: Optional[str] = "fake"
    AUDIO_API_BASE_URL: Optional[str] = None
    AUDIO_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_prefix="QUILLMUSIC_",
    )


settings = Settings()
