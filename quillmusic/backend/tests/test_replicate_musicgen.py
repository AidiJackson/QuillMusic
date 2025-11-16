"""
Tests for Replicate MusicGen integration
"""
import pytest
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.providers.replicate_musicgen import ReplicateMusicGenClient, ReplicateMusicGenError
from app.core.config import Settings, InstrumentalEngineConfig

client = TestClient(app)


@pytest.mark.asyncio
async def test_replicate_musicgen_success():
    """Test successful Replicate MusicGen API call with polling."""
    settings = Settings(
        REPLICATE_API_TOKEN="r8_test_token",
        REPLICATE_BASE_URL="https://api.replicate.com",
        REPLICATE_MUSICGEN_VERSION="test-version-123",
    )

    replicate_client = ReplicateMusicGenClient(settings=settings)

    # Mock httpx.AsyncClient
    with patch("app.providers.replicate_musicgen.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock prediction creation response
        mock_create_response = Mock()
        mock_create_response.status_code = 201
        mock_create_response.json.return_value = {
            "id": "pred_abc123",
            "status": "starting",
        }

        # Mock first poll: still processing
        mock_poll_response_1 = Mock()
        mock_poll_response_1.status_code = 200
        mock_poll_response_1.json.return_value = {
            "id": "pred_abc123",
            "status": "processing",
        }

        # Mock second poll: succeeded
        mock_poll_response_2 = Mock()
        mock_poll_response_2.status_code = 200
        mock_poll_response_2.json.return_value = {
            "id": "pred_abc123",
            "status": "succeeded",
            "output": "https://replicate.delivery/test-music.wav",
        }

        # Set up mock responses in sequence
        mock_client.post = AsyncMock(return_value=mock_create_response)
        mock_client.get = AsyncMock(side_effect=[mock_poll_response_1, mock_poll_response_2])

        # Call generate_audio
        audio_url = await replicate_client.generate_audio(
            prompt="upbeat electronic dance music",
            duration_seconds=30,
            poll_interval=0.01,  # Fast polling for tests
        )

        # Verify result
        assert audio_url == "https://replicate.delivery/test-music.wav"

        # Verify API calls
        mock_client.post.assert_called_once()
        create_call_args = mock_client.post.call_args
        assert create_call_args[0][0] == "https://api.replicate.com/v1/predictions"
        assert create_call_args[1]["headers"]["Authorization"] == "Token r8_test_token"
        assert create_call_args[1]["json"]["version"] == "test-version-123"
        assert create_call_args[1]["json"]["input"]["prompt"] == "upbeat electronic dance music"
        assert create_call_args[1]["json"]["input"]["duration"] == 30

        # Verify polling occurred (2 GET calls)
        assert mock_client.get.call_count == 2


@pytest.mark.asyncio
async def test_replicate_musicgen_output_list():
    """Test Replicate MusicGen handles output as list."""
    settings = Settings(
        REPLICATE_API_TOKEN="r8_test_token",
        REPLICATE_MUSICGEN_VERSION="test-version-123",
    )

    replicate_client = ReplicateMusicGenClient(settings=settings)

    with patch("app.providers.replicate_musicgen.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_create_response = Mock()
        mock_create_response.status_code = 201
        mock_create_response.json.return_value = {
            "id": "pred_xyz789",
            "status": "starting",
        }

        # Mock poll response with output as list
        mock_poll_response = Mock()
        mock_poll_response.status_code = 200
        mock_poll_response.json.return_value = {
            "id": "pred_xyz789",
            "status": "succeeded",
            "output": ["https://replicate.delivery/music-track.mp3"],  # List format
        }

        mock_client.post = AsyncMock(return_value=mock_create_response)
        mock_client.get = AsyncMock(return_value=mock_poll_response)

        audio_url = await replicate_client.generate_audio(
            prompt="test prompt",
            poll_interval=0.01,
        )

        assert audio_url == "https://replicate.delivery/music-track.mp3"


@pytest.mark.asyncio
async def test_replicate_musicgen_missing_token():
    """Test Replicate MusicGen error when token is missing."""
    settings = Settings(
        REPLICATE_API_TOKEN=None,
        REPLICATE_MUSICGEN_VERSION="test-version-123",
    )

    with pytest.raises(ReplicateMusicGenError, match="API token is not configured"):
        ReplicateMusicGenClient(settings=settings)


@pytest.mark.asyncio
async def test_replicate_musicgen_missing_version():
    """Test Replicate MusicGen error when version is missing."""
    settings = Settings(
        REPLICATE_API_TOKEN="r8_test_token",
        REPLICATE_MUSICGEN_VERSION=None,
    )

    with pytest.raises(ReplicateMusicGenError, match="version is not configured"):
        ReplicateMusicGenClient(settings=settings)


@pytest.mark.asyncio
async def test_replicate_musicgen_prediction_failed():
    """Test Replicate MusicGen handles failed predictions."""
    settings = Settings(
        REPLICATE_API_TOKEN="r8_test_token",
        REPLICATE_MUSICGEN_VERSION="test-version-123",
    )

    replicate_client = ReplicateMusicGenClient(settings=settings)

    with patch("app.providers.replicate_musicgen.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_create_response = Mock()
        mock_create_response.status_code = 201
        mock_create_response.json.return_value = {
            "id": "pred_fail",
            "status": "starting",
        }

        # Mock poll response with failed status
        mock_poll_response = Mock()
        mock_poll_response.status_code = 200
        mock_poll_response.json.return_value = {
            "id": "pred_fail",
            "status": "failed",
            "error": "Model inference failed: out of memory",
        }

        mock_client.post = AsyncMock(return_value=mock_create_response)
        mock_client.get = AsyncMock(return_value=mock_poll_response)

        with pytest.raises(ReplicateMusicGenError, match="failed.*out of memory"):
            await replicate_client.generate_audio(
                prompt="test prompt",
                poll_interval=0.01,
            )


@pytest.mark.asyncio
async def test_replicate_musicgen_timeout():
    """Test Replicate MusicGen handles timeouts."""
    settings = Settings(
        REPLICATE_API_TOKEN="r8_test_token",
        REPLICATE_MUSICGEN_VERSION="test-version-123",
    )

    replicate_client = ReplicateMusicGenClient(settings=settings)

    with patch("app.providers.replicate_musicgen.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_create_response = Mock()
        mock_create_response.status_code = 201
        mock_create_response.json.return_value = {
            "id": "pred_timeout",
            "status": "starting",
        }

        # Mock poll response that stays in processing state
        mock_poll_response = Mock()
        mock_poll_response.status_code = 200
        mock_poll_response.json.return_value = {
            "id": "pred_timeout",
            "status": "processing",
        }

        mock_client.post = AsyncMock(return_value=mock_create_response)
        mock_client.get = AsyncMock(return_value=mock_poll_response)

        with pytest.raises(ReplicateMusicGenError, match="timed out"):
            await replicate_client.generate_audio(
                prompt="test prompt",
                poll_interval=0.01,
                timeout=0.1,  # Very short timeout
            )


@pytest.mark.asyncio
async def test_replicate_musicgen_http_error():
    """Test Replicate MusicGen handles HTTP errors."""
    settings = Settings(
        REPLICATE_API_TOKEN="r8_test_token",
        REPLICATE_MUSICGEN_VERSION="test-version-123",
    )

    replicate_client = ReplicateMusicGenClient(settings=settings)

    with patch("app.providers.replicate_musicgen.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock 401 Unauthorized response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized: Invalid API token"
        mock_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(ReplicateMusicGenError, match="status 401"):
            await replicate_client.generate_audio(prompt="test prompt")


def test_config_endpoint_includes_replicate_musicgen():
    """Test config endpoint includes Replicate MusicGen when configured."""
    with patch("app.api.routes.config.settings") as mock_settings:
        # Mock settings properties
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
                name="replicate_musicgen",
                label="Replicate MusicGen (Cloud)",
                engine_type="replicate_musicgen",
                base_url="https://api.replicate.com",
                api_key="r8_test",
                model="test-version-123",
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

        # Check replicate musicgen engine
        replicate_engine = next(e for e in engines if e["name"] == "replicate_musicgen")
        assert replicate_engine["label"] == "Replicate MusicGen (Cloud)"
        assert replicate_engine["engine_type"] == "replicate_musicgen"
        assert replicate_engine["available"] is True


def test_config_endpoint_excludes_replicate_musicgen_when_not_configured():
    """Test config endpoint excludes Replicate MusicGen when not configured."""
    with patch("app.api.routes.config.settings") as mock_settings:
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
        ]

        response = client.get("/api/config/")
        assert response.status_code == 200

        data = response.json()
        engines = data["features"]["instrumental_engines"]

        # Should only have fake engine
        assert len(engines) == 1
        assert engines[0]["name"] == "fake"
