"""
QuillMusic Backend Configuration
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class InstrumentalEngineConfig(BaseModel):
    """Configuration for a single instrumental engine."""
    name: str
    label: str
    engine_type: str  # "fake" or "external_http"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None


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

    # Audio Provider Configuration (for instrumental rendering - legacy)
    AUDIO_PROVIDER: Optional[str] = "fake"
    AUDIO_API_BASE_URL: Optional[str] = None
    AUDIO_API_KEY: Optional[str] = None

    # Instrumental Engine Configuration (multi-engine support)
    INSTRUMENTAL_ENGINES: Optional[str] = None  # Comma-separated list of engine names
    DEFAULT_INSTRUMENTAL_MODEL: Optional[str] = None

    # Stable Audio API Configuration (hosted API)
    STABLE_AUDIO_API_BASE_URL: Optional[str] = None
    STABLE_AUDIO_API_KEY: Optional[str] = None
    STABLE_AUDIO_API_MODEL: str = "stable-audio-1.0"

    # Stable Audio Open Configuration (self-hosted)
    STABLE_AUDIO_OPEN_BASE_URL: Optional[str] = None
    STABLE_AUDIO_OPEN_API_KEY: Optional[str] = None
    STABLE_AUDIO_OPEN_MODEL: str = "stable-audio-open-1.0"

    # MusicGen Configuration (self-hosted)
    MUSICGEN_BASE_URL: Optional[str] = None
    MUSICGEN_API_KEY: Optional[str] = None
    MUSICGEN_MODEL: str = "musicgen-medium"

    # ElevenLabs TTS Configuration (vocal synthesis)
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_BASE_URL: str = "https://api.elevenlabs.io"
    ELEVENLABS_DEFAULT_MODEL: str = "eleven_turbo_v2_5"
    ELEVENLABS_DEFAULT_VOICE_ID: Optional[str] = None

    # Replicate Configuration (hosted MusicGen)
    REPLICATE_API_TOKEN: Optional[str] = None
    REPLICATE_BASE_URL: str = "https://api.replicate.com"
    REPLICATE_MUSICGEN_VERSION: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_prefix="QUILLMUSIC_",
        # Allow fallback to REPLICATE_API_TOKEN if QUILLMUSIC_REPLICATE_API_TOKEN is not set
        extra="ignore",
    )

    @field_validator('REPLICATE_API_TOKEN', mode='before')
    @classmethod
    def fallback_replicate_token(cls, v):
        """Fallback to REPLICATE_API_TOKEN if QUILLMUSIC_REPLICATE_API_TOKEN is not set."""
        if v is None:
            return os.getenv('REPLICATE_API_TOKEN')
        return v

    @property
    def instrumental_engines(self) -> list[InstrumentalEngineConfig]:
        """
        Build list of available instrumental engines based on configuration.

        Returns:
            List of configured instrumental engines
        """
        engines = []

        # Always include fake engine for dev/test
        engines.append(InstrumentalEngineConfig(
            name="fake",
            label="Fake Demo Engine (Dev/Test)",
            engine_type="fake",
        ))

        # Add Stable Audio API if configured
        if self.STABLE_AUDIO_API_BASE_URL:
            engines.append(InstrumentalEngineConfig(
                name="stable_audio_api",
                label="Stable Audio (Hosted API)",
                engine_type="external_http",
                base_url=self.STABLE_AUDIO_API_BASE_URL,
                api_key=self.STABLE_AUDIO_API_KEY,
                model=self.STABLE_AUDIO_API_MODEL,
            ))

        # Add Stable Audio Open if configured
        if self.STABLE_AUDIO_OPEN_BASE_URL:
            engines.append(InstrumentalEngineConfig(
                name="stable_audio_open",
                label="Stable Audio Open (Self-Hosted)",
                engine_type="external_http",
                base_url=self.STABLE_AUDIO_OPEN_BASE_URL,
                api_key=self.STABLE_AUDIO_OPEN_API_KEY,
                model=self.STABLE_AUDIO_OPEN_MODEL,
            ))

        # Add MusicGen if configured
        if self.MUSICGEN_BASE_URL:
            engines.append(InstrumentalEngineConfig(
                name="musicgen",
                label="MusicGen (Self-Hosted)",
                engine_type="external_http",
                base_url=self.MUSICGEN_BASE_URL,
                api_key=self.MUSICGEN_API_KEY,
                model=self.MUSICGEN_MODEL,
            ))

        # Add Replicate MusicGen if configured
        if self.REPLICATE_API_TOKEN and self.REPLICATE_MUSICGEN_VERSION:
            engines.append(InstrumentalEngineConfig(
                name="replicate_musicgen",
                label="Replicate MusicGen (Cloud)",
                engine_type="replicate_musicgen",
                base_url=self.REPLICATE_BASE_URL,
                api_key=self.REPLICATE_API_TOKEN,
                model=self.REPLICATE_MUSICGEN_VERSION,
            ))

        # Filter by INSTRUMENTAL_ENGINES if specified
        if self.INSTRUMENTAL_ENGINES:
            enabled_names = [name.strip() for name in self.INSTRUMENTAL_ENGINES.split(",")]
            engines = [e for e in engines if e.name in enabled_names]

        return engines

    def get_engine_config(self, engine_name: str) -> Optional[InstrumentalEngineConfig]:
        """
        Get configuration for a specific engine by name.

        Args:
            engine_name: Name of the engine (e.g., "stable_audio_api")

        Returns:
            Engine configuration or None if not found
        """
        for engine in self.instrumental_engines:
            if engine.name == engine_name:
                return engine
        return None


settings = Settings()
