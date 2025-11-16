"""
Config and feature flags API routes
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.core.config import settings

router = APIRouter(prefix="/config", tags=["config"])


class AudioProviderInfo(BaseModel):
    """Information about configured audio provider."""
    provider: str = Field(..., description="Audio provider type (fake or stable_audio_http)")
    available: bool = Field(..., description="Whether external audio is properly configured")
    models: list[str] = Field(default_factory=list, description="Available AI models")


class FeatureFlags(BaseModel):
    """Feature flags for the frontend."""
    external_instrumental_available: bool = Field(..., description="External instrumental rendering is configured")
    audio_provider: AudioProviderInfo = Field(..., description="Audio provider information")


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
    # Check if external audio is properly configured
    external_available = (
        settings.AUDIO_PROVIDER == "stable_audio_http"
        and settings.AUDIO_API_BASE_URL is not None
        and settings.AUDIO_API_KEY is not None
    )

    # Determine available models based on provider
    available_models = []
    if settings.AUDIO_PROVIDER == "stable_audio_http":
        # For stable_audio_http provider, offer these models
        # In a real implementation, this could be fetched from the provider's API
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

    return AppConfig(
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        features=FeatureFlags(
            external_instrumental_available=external_available,
            audio_provider=AudioProviderInfo(
                provider=settings.AUDIO_PROVIDER or "fake",
                available=external_available,
                models=available_models,
            ),
        ),
    )
