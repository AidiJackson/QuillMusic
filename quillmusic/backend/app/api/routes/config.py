"""
Config and feature flags API routes
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.core.config import settings

router = APIRouter(prefix="/config", tags=["config"])


class InstrumentalEngineInfo(BaseModel):
    """Information about an instrumental engine."""
    name: str = Field(..., description="Engine identifier (e.g., 'fake', 'stable_audio_api')")
    label: str = Field(..., description="Human-readable label for the UI")
    engine_type: str = Field(..., description="Engine type ('fake' or 'external_http')")
    available: bool = Field(..., description="Whether the engine is properly configured and available")


class AudioProviderInfo(BaseModel):
    """Information about configured audio provider (legacy)."""
    provider: str = Field(..., description="Audio provider type (fake or stable_audio_http)")
    available: bool = Field(..., description="Whether external audio is properly configured")
    models: list[str] = Field(default_factory=list, description="Available AI models")


class FeatureFlags(BaseModel):
    """Feature flags for the frontend."""
    external_instrumental_available: bool = Field(..., description="External instrumental rendering is configured")
    audio_provider: AudioProviderInfo = Field(..., description="Audio provider information (legacy)")
    instrumental_engines: list[InstrumentalEngineInfo] = Field(..., description="Available instrumental engines")


class AppConfig(BaseModel):
    """Application configuration exposed to frontend."""
    app_name: str = Field(..., description="Application name")
    app_version: str = Field(..., description="Application version")
    features: FeatureFlags = Field(..., description="Feature flags")


@router.get("/", response_model=AppConfig)
async def get_config():
    """
    Get application configuration and feature flags.

    This endpoint allows the frontend to discover what features are available
    based on backend configuration.
    """
    # Check if external audio is properly configured (legacy)
    external_available = (
        settings.AUDIO_PROVIDER == "stable_audio_http"
        and settings.AUDIO_API_BASE_URL is not None
        and settings.AUDIO_API_KEY is not None
    )

    # Determine available models based on provider (legacy)
    available_models = []
    if settings.AUDIO_PROVIDER == "stable_audio_http":
        available_models = [
            "Stable Audio 2.0",
            "Stable Audio Open",
        ]
    elif settings.AUDIO_PROVIDER == "musicgen":
        available_models = [
            "MusicGen Small",
            "MusicGen Medium",
            "MusicGen Large",
        ]

    # Build list of instrumental engines from config
    instrumental_engines = []
    for engine_config in settings.instrumental_engines:
        # Engine is available if it's fake or has base_url configured
        is_available = (
            engine_config.engine_type == "fake" or
            engine_config.base_url is not None
        )

        instrumental_engines.append(InstrumentalEngineInfo(
            name=engine_config.name,
            label=engine_config.label,
            engine_type=engine_config.engine_type,
            available=is_available,
        ))

    # Check if any external engine is available
    any_external_available = any(
        e.engine_type == "external_http" and e.available
        for e in instrumental_engines
    )

    return AppConfig(
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        features=FeatureFlags(
            external_instrumental_available=external_available or any_external_available,
            audio_provider=AudioProviderInfo(
                provider=settings.AUDIO_PROVIDER or "fake",
                available=external_available,
                models=available_models,
            ),
            instrumental_engines=instrumental_engines,
        ),
    )
