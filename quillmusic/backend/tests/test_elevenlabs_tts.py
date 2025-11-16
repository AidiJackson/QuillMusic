"""
Tests for ElevenLabs TTS integration
"""
import pytest
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.providers.elevenlabs_tts import ElevenLabsClient, ElevenLabsTTSError

client = TestClient(app)


@pytest.mark.asyncio
async def test_elevenlabs_client_success():
    """Test successful ElevenLabs TTS generation."""
    # Create client
    tts_client = ElevenLabsClient(
        api_key="test-api-key",
        base_url="https://api.elevenlabs.io",
        default_model="eleven_turbo_v2_5",
    )

    # Mock httpx.AsyncClient
    with patch("app.providers.elevenlabs_tts.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"FAKE_AUDIO_BYTES"
        mock_client.post = AsyncMock(return_value=mock_response)

        # Call generate_speech
        audio_bytes = await tts_client.generate_speech(
            text="Hello world",
            voice_id="test-voice-id",
        )

        # Verify result
        assert audio_bytes == b"FAKE_AUDIO_BYTES"

        # Verify API call
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://api.elevenlabs.io/v1/text-to-speech/test-voice-id"
        assert call_args[1]["headers"]["xi-api-key"] == "test-api-key"
        assert call_args[1]["json"]["model_id"] == "eleven_turbo_v2_5"
        assert call_args[1]["json"]["text"] == "Hello world"


@pytest.mark.asyncio
async def test_elevenlabs_client_custom_model():
    """Test ElevenLabs TTS with custom model ID."""
    tts_client = ElevenLabsClient(
        api_key="test-api-key",
        base_url="https://api.elevenlabs.io",
        default_model="eleven_turbo_v2_5",
    )

    with patch("app.providers.elevenlabs_tts.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"AUDIO"
        mock_client.post = AsyncMock(return_value=mock_response)

        await tts_client.generate_speech(
            text="Test",
            voice_id="voice-123",
            model_id="eleven_multilingual_v2",
        )

        # Verify custom model was used
        call_args = mock_client.post.call_args
        assert call_args[1]["json"]["model_id"] == "eleven_multilingual_v2"


@pytest.mark.asyncio
async def test_elevenlabs_client_empty_text():
    """Test ElevenLabs TTS rejects empty text."""
    tts_client = ElevenLabsClient(
        api_key="test-api-key",
        base_url="https://api.elevenlabs.io",
        default_model="eleven_turbo_v2_5",
    )

    with pytest.raises(ElevenLabsTTSError, match="Text cannot be empty"):
        await tts_client.generate_speech(
            text="",
            voice_id="voice-123",
        )


@pytest.mark.asyncio
async def test_elevenlabs_client_empty_voice_id():
    """Test ElevenLabs TTS rejects empty voice ID."""
    tts_client = ElevenLabsClient(
        api_key="test-api-key",
        base_url="https://api.elevenlabs.io",
        default_model="eleven_turbo_v2_5",
    )

    with pytest.raises(ElevenLabsTTSError, match="Voice ID cannot be empty"):
        await tts_client.generate_speech(
            text="Hello",
            voice_id="",
        )


@pytest.mark.asyncio
async def test_elevenlabs_client_http_error():
    """Test ElevenLabs TTS handles HTTP errors."""
    tts_client = ElevenLabsClient(
        api_key="test-api-key",
        base_url="https://api.elevenlabs.io",
        default_model="eleven_turbo_v2_5",
    )

    with patch("app.providers.elevenlabs_tts.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized: Invalid API key"
        mock_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(ElevenLabsTTSError, match="status 401"):
            await tts_client.generate_speech(
                text="Hello",
                voice_id="voice-123",
            )


def test_vocal_preview_endpoint_missing_api_key():
    """Test vocal preview endpoint returns 500 when API key not configured."""
    with patch("app.api.routes.vocals.settings") as mock_settings:
        mock_settings.ELEVENLABS_API_KEY = None

        response = client.post(
            "/api/vocals/preview",
            json={
                "text": "Hello world",
                "voice_id": "test-voice",
            },
        )

        assert response.status_code == 500
        assert "API key not configured" in response.json()["detail"]


def test_vocal_preview_endpoint_success():
    """Test successful vocal preview generation."""
    with patch("app.api.routes.vocals.settings") as mock_settings:
        mock_settings.ELEVENLABS_API_KEY = "test-key"
        mock_settings.ELEVENLABS_BASE_URL = "https://api.elevenlabs.io"
        mock_settings.ELEVENLABS_DEFAULT_MODEL = "eleven_turbo_v2_5"

        # Mock the ElevenLabs client
        with patch("app.api.routes.vocals.ElevenLabsClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Mock async method
            async def mock_generate(*args, **kwargs):
                return b"FAKE_AUDIO_DATA"

            mock_client.generate_speech = mock_generate

            response = client.post(
                "/api/vocals/preview",
                json={
                    "text": "Hello world, this is a test",
                    "voice_id": "test-voice-id",
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "audio/mpeg"
            assert response.content == b"FAKE_AUDIO_DATA"


def test_vocal_preview_endpoint_validation():
    """Test vocal preview endpoint validates input."""
    with patch("app.api.routes.vocals.settings") as mock_settings:
        mock_settings.ELEVENLABS_API_KEY = "test-key"

        # Empty text
        response = client.post(
            "/api/vocals/preview",
            json={
                "text": "",
                "voice_id": "voice-123",
            },
        )
        assert response.status_code == 422  # Validation error

        # Missing voice_id
        response = client.post(
            "/api/vocals/preview",
            json={
                "text": "Hello",
            },
        )
        assert response.status_code == 422  # Validation error


def test_vocal_preview_endpoint_tts_error():
    """Test vocal preview endpoint handles TTS errors gracefully."""
    with patch("app.api.routes.vocals.settings") as mock_settings:
        mock_settings.ELEVENLABS_API_KEY = "test-key"
        mock_settings.ELEVENLABS_BASE_URL = "https://api.elevenlabs.io"
        mock_settings.ELEVENLABS_DEFAULT_MODEL = "eleven_turbo_v2_5"

        with patch("app.api.routes.vocals.ElevenLabsClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Mock async method that raises error
            async def mock_generate(*args, **kwargs):
                from app.providers.elevenlabs_tts import ElevenLabsTTSError
                raise ElevenLabsTTSError("API quota exceeded")

            mock_client.generate_speech = mock_generate

            response = client.post(
                "/api/vocals/preview",
                json={
                    "text": "Test text",
                    "voice_id": "voice-123",
                },
            )

            assert response.status_code == 502
            assert "Failed to generate vocals" in response.json()["detail"]
