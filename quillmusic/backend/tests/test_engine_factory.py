"""
Tests for song blueprint engine factory and dependency injection
"""
import pytest
from unittest.mock import patch, MagicMock
from app.core.config import Settings
from app.core.dependencies import get_song_blueprint_engine
from app.services.song_blueprint_service import (
    FakeSongBlueprintEngine,
    LLMSongBlueprintEngine,
)


def test_factory_returns_fake_engine_by_default():
    """Test that factory returns FakeSongBlueprintEngine by default."""
    # Default settings should use fake mode
    engine = get_song_blueprint_engine()

    assert isinstance(engine, FakeSongBlueprintEngine)
    assert not isinstance(engine, LLMSongBlueprintEngine)


def test_factory_returns_fake_when_mode_is_fake():
    """Test factory returns fake engine when mode is explicitly 'fake'."""
    with patch("app.core.dependencies.settings") as mock_settings:
        mock_settings.SONG_ENGINE_MODE = "fake"

        engine = get_song_blueprint_engine()

        assert isinstance(engine, FakeSongBlueprintEngine)


def test_factory_returns_fake_when_llm_mode_but_no_api_key():
    """Test factory returns fake engine when LLM mode but no API key."""
    with patch("app.core.dependencies.settings") as mock_settings:
        mock_settings.SONG_ENGINE_MODE = "llm"
        mock_settings.LLM_API_KEY = None  # No API key

        engine = get_song_blueprint_engine()

        # Should fall back to fake engine
        assert isinstance(engine, FakeSongBlueprintEngine)


def test_factory_returns_llm_engine_when_configured():
    """Test factory returns LLM engine when properly configured."""
    with patch("app.core.dependencies.settings") as mock_settings:
        mock_settings.SONG_ENGINE_MODE = "llm"
        mock_settings.LLM_API_KEY = "test-api-key"
        mock_settings.LLM_API_BASE = None
        mock_settings.LLM_MODEL_NAME = "gpt-4.1-mini"
        mock_settings.LLM_PROVIDER = "openai-compatible"

        # Mock the LLM client creation to avoid actual API calls
        with patch("app.services.llm_client.create_llm_client") as mock_create:
            mock_llm_client = MagicMock()
            mock_create.return_value = mock_llm_client

            engine = get_song_blueprint_engine()

            # Should return LLM engine
            assert isinstance(engine, LLMSongBlueprintEngine)

            # Verify create_llm_client was called with correct params
            mock_create.assert_called_once_with(
                api_key="test-api-key",
                model_name="gpt-4.1-mini",
                api_base=None,
                provider="openai-compatible",
            )


def test_factory_handles_llm_creation_error():
    """Test factory falls back to fake engine if LLM creation fails."""
    with patch("app.core.dependencies.settings") as mock_settings:
        mock_settings.SONG_ENGINE_MODE = "llm"
        mock_settings.LLM_API_KEY = "test-api-key"
        mock_settings.LLM_MODEL_NAME = "gpt-4.1-mini"
        mock_settings.LLM_PROVIDER = "openai-compatible"

        # Mock create_llm_client to raise an exception
        with patch("app.services.llm_client.create_llm_client") as mock_create:
            mock_create.side_effect = Exception("Failed to create LLM client")

            engine = get_song_blueprint_engine()

            # Should fall back to fake engine
            assert isinstance(engine, FakeSongBlueprintEngine)


def test_settings_validation():
    """Test that Settings model validates configuration correctly."""
    # Test default settings
    settings = Settings()
    assert settings.SONG_ENGINE_MODE == "fake"
    assert settings.LLM_API_KEY is None

    # Test LLM mode settings
    settings_llm = Settings(
        SONG_ENGINE_MODE="llm",
        LLM_API_KEY="sk-test123",
        LLM_MODEL_NAME="gpt-4",
    )
    assert settings_llm.SONG_ENGINE_MODE == "llm"
    assert settings_llm.LLM_API_KEY == "sk-test123"
    assert settings_llm.LLM_MODEL_NAME == "gpt-4"


def test_settings_with_env_prefix():
    """Test that settings use QUILLMUSIC_ prefix correctly."""
    import os

    # Set environment variables with prefix
    os.environ["QUILLMUSIC_SONG_ENGINE_MODE"] = "llm"
    os.environ["QUILLMUSIC_LLM_API_KEY"] = "test-key-123"

    try:
        # Create new settings instance
        settings = Settings()

        assert settings.SONG_ENGINE_MODE == "llm"
        assert settings.LLM_API_KEY == "test-key-123"
    finally:
        # Clean up
        os.environ.pop("QUILLMUSIC_SONG_ENGINE_MODE", None)
        os.environ.pop("QUILLMUSIC_LLM_API_KEY", None)
