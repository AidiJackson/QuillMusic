"""
QuillMusic Backend Dependencies
"""
from typing import Generator, Optional
import logging
import redis
from redis import Redis
from rq import Queue

from app.core.config import settings, Settings

logger = logging.getLogger(__name__)


# Redis connection pool (singleton pattern)
_redis_client: Optional[Redis] = None


def get_redis() -> Redis:
    """Get Redis connection."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _redis_client


def get_render_queue() -> Queue:
    """Get RQ queue for render jobs."""
    redis_conn = get_redis()
    return Queue("renders", connection=redis_conn)


def get_blueprint_queue() -> Queue:
    """Get RQ queue for blueprint generation jobs."""
    redis_conn = get_redis()
    return Queue("blueprints", connection=redis_conn)


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def get_song_blueprint_engine():
    """
    Get the configured song blueprint engine.

    This is a dependency injection function for FastAPI routes.
    Returns the appropriate engine based on configuration.

    Returns:
        SongBlueprintEngine: Either FakeSongBlueprintEngine or LLMSongBlueprintEngine
    """
    from app.services.song_blueprint_service import (
        FakeSongBlueprintEngine,
        LLMSongBlueprintEngine,
        SongBlueprintEngine,
    )
    from app.services.llm_client import create_llm_client

    # Default to fake engine
    if settings.SONG_ENGINE_MODE != "llm":
        logger.info("Using FakeSongBlueprintEngine (mode=%s)", settings.SONG_ENGINE_MODE)
        return FakeSongBlueprintEngine()

    # Check if LLM configuration is present
    if not settings.LLM_API_KEY:
        logger.warning(
            "SONG_ENGINE_MODE is 'llm' but no LLM_API_KEY configured. "
            "Falling back to FakeSongBlueprintEngine."
        )
        return FakeSongBlueprintEngine()

    # Create LLM-based engine
    try:
        logger.info(
            "Creating LLMSongBlueprintEngine (provider=%s, model=%s)",
            settings.LLM_PROVIDER,
            settings.LLM_MODEL_NAME,
        )

        llm_client = create_llm_client(
            api_key=settings.LLM_API_KEY,
            model_name=settings.LLM_MODEL_NAME,
            api_base=settings.LLM_API_BASE,
            provider=settings.LLM_PROVIDER,
        )

        return LLMSongBlueprintEngine(
            llm_client=llm_client,
            fallback_engine=FakeSongBlueprintEngine(),
        )

    except Exception as e:
        logger.error(
            f"Failed to create LLM engine, falling back to fake engine: {e}"
        )
        return FakeSongBlueprintEngine()
