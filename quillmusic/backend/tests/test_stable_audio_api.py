"""
Tests for Stable Audio API integration
"""
import pytest
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.providers.stable_audio_api import generate_stable_audio, StableAudioAPIError
from app.core.config import InstrumentalEngineConfig

client = TestClient(app)


@pytest.mark.asyncio
async def test_stable_audio_api_success():
    """Test successful Stable Audio API call."""
    engine_config = InstrumentalEngineConfig(
        name="stable_audio_api",
        label="Stable Audio (Hosted API)",
        engine_type="external_http",
        base_url="https://api.stableaudio.com",
        api_key="sk-test-key",
        model="stable-audio-1.0",
    )

    # Mock httpx.AsyncClient
    with patch("app.providers.stable_audio_api.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ready",
            "audio_url": "https://cdn.stableaudio.com/test-track.wav",
        }
        mock_client.post = AsyncMock(return_value=mock_response)

        # Call generate_stable_audio
        audio_url = await generate_stable_audio(
            engine_config=engine_config,
            prompt="epic orchestral battle music",
            duration_seconds=30,
        )

        # Verify result
        assert audio_url == "https://cdn.stableaudio.com/test-track.wav"

        # Verify API call
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://api.stableaudio.com/v2/generate/audio"
        assert call_args[1]["headers"]["Authorization"] == "Bearer sk-test-key"
        assert call_args[1]["json"]["model"] == "stable-audio-1.0"
        assert call_args[1]["json"]["prompt"] == "epic orchestral battle music"
        assert call_args[1]["json"]["seconds_total"] == 30


@pytest.mark.asyncio
async def test_stable_audio_api_missing_base_url():
    """Test Stable Audio API error when base_url is missing."""
    engine_config = InstrumentalEngineConfig(
        name="stable_audio_api",
        label="Stable Audio (Hosted API)",
        engine_type="external_http",
        base_url=None,
        api_key="sk-test-key",
        model="stable-audio-1.0",
    )

    with pytest.raises(StableAudioAPIError, match="base_url is not configured"):
        await generate_stable_audio(
            engine_config=engine_config,
            prompt="test prompt",
            duration_seconds=30,
        )


@pytest.mark.asyncio
async def test_stable_audio_api_missing_api_key():
    """Test Stable Audio API error when api_key is missing."""
    engine_config = InstrumentalEngineConfig(
        name="stable_audio_api",
        label="Stable Audio (Hosted API)",
        engine_type="external_http",
        base_url="https://api.stableaudio.com",
        api_key=None,
        model="stable-audio-1.0",
    )

    with pytest.raises(StableAudioAPIError, match="api_key is not configured"):
        await generate_stable_audio(
            engine_config=engine_config,
            prompt="test prompt",
            duration_seconds=30,
        )


@pytest.mark.asyncio
async def test_stable_audio_api_http_error():
    """Test Stable Audio API handles HTTP errors."""
    engine_config = InstrumentalEngineConfig(
        name="stable_audio_api",
        label="Stable Audio (Hosted API)",
        engine_type="external_http",
        base_url="https://api.stableaudio.com",
        api_key="sk-test-key",
        model="stable-audio-1.0",
    )

    with patch("app.providers.stable_audio_api.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized: Invalid API key"
        mock_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(StableAudioAPIError, match="status 401"):
            await generate_stable_audio(
                engine_config=engine_config,
                prompt="test prompt",
                duration_seconds=30,
            )


@pytest.mark.asyncio
async def test_stable_audio_api_invalid_response():
    """Test Stable Audio API handles invalid response format."""
    engine_config = InstrumentalEngineConfig(
        name="stable_audio_api",
        label="Stable Audio (Hosted API)",
        engine_type="external_http",
        base_url="https://api.stableaudio.com",
        api_key="sk-test-key",
        model="stable-audio-1.0",
    )

    with patch("app.providers.stable_audio_api.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock response with unexpected format
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "pending",  # Not "ready"
            # Missing audio_url
        }
        mock_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(StableAudioAPIError, match="unexpected response"):
            await generate_stable_audio(
                engine_config=engine_config,
                prompt="test prompt",
                duration_seconds=30,
            )


def test_config_endpoint_includes_stable_audio_api():
    """Test config endpoint includes Stable Audio API when configured."""
    with patch("app.api.routes.config.settings") as mock_settings:
        # Mock instrumental_engines property
        mock_settings.APP_NAME = "QuillMusic"
        mock_settings.APP_VERSION = "0.1.0"
        mock_settings.AUDIO_PROVIDER = "fake"
        mock_settings.AUDIO_API_BASE_URL = None
        mock_settings.AUDIO_API_KEY = None
        mock_settings.instrumental_engines = [
            InstrumentalEngineConfig(
                name="fake",
                label="Fake Demo Engine (Dev/Test)",
                engine_type="fake",
            ),
            InstrumentalEngineConfig(
                name="stable_audio_api",
                label="Stable Audio (Hosted API)",
                engine_type="external_http",
                base_url="https://api.stableaudio.com",
                api_key="sk-test",
                model="stable-audio-1.0",
            ),
        ]

        # Get config
        response = client.get("/api/config/")
        assert response.status_code == 200

        data = response.json()
        assert "features" in data
        assert "instrumental_engines" in data["features"]

        engines = data["features"]["instrumental_engines"]
        assert len(engines) == 2

        # Check fake engine
        fake_engine = next(e for e in engines if e["name"] == "fake")
        assert fake_engine["label"] == "Fake Demo Engine (Dev/Test)"
        assert fake_engine["engine_type"] == "fake"
        assert fake_engine["available"] is True

        # Check stable audio api engine
        stable_engine = next(e for e in engines if e["name"] == "stable_audio_api")
        assert stable_engine["label"] == "Stable Audio (Hosted API)"
        assert stable_engine["engine_type"] == "external_http"
        assert stable_engine["available"] is True


def test_instrumental_render_with_stable_audio_api():
    """Test instrumental rendering with Stable Audio API engine."""
    # Create a blueprint
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "An epic orchestral piece",
            "genre": "Classical",
            "mood": "Epic",
            "bpm": 100,
            "key": "Cm",
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Mock settings and API call
    with patch("app.services.instrumental_render_service.settings") as mock_settings:
        # Configure stable audio api engine
        mock_settings.get_engine_config = Mock(return_value=InstrumentalEngineConfig(
            name="stable_audio_api",
            label="Stable Audio (Hosted API)",
            engine_type="external_http",
            base_url="https://api.stableaudio.com",
            api_key="sk-test-key",
            model="stable-audio-1.0",
        ))

        # Mock the async API call
        with patch("app.providers.stable_audio_api.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "ready",
                "audio_url": "https://cdn.stableaudio.com/epic-orchestral.wav",
            }
            mock_client.post = AsyncMock(return_value=mock_response)

            # Render with stable_audio_api engine
            render_response = client.post(
                "/api/instrumental/render",
                json={
                    "source_type": "blueprint",
                    "source_id": blueprint_id,
                    "engine_type": "external_http",
                    "model": "stable_audio_api",
                },
            )

            assert render_response.status_code == 200
            data = render_response.json()
            assert data["status"] == "ready"
            assert data["audio_url"] == "https://cdn.stableaudio.com/epic-orchestral.wav"
            assert data["model"] == "stable_audio_api"
            assert data["error_message"] is None
