"""
Tests for MusicGen instrumental engine configuration
"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import InstrumentalEngineConfig

client = TestClient(app)


def test_musicgen_config_when_base_url_set():
    """Test MusicGen engine appears in config when BASE_URL is set."""
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
            InstrumentalEngineConfig(
                name="musicgen",
                label="MusicGen (Self-Hosted)",
                engine_type="external_http",
                base_url="https://musicgen.example.com",
                api_key=None,
                model="facebook/musicgen-medium",
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

        # Check MusicGen engine
        musicgen_engine = next(e for e in engines if e["name"] == "musicgen")
        assert musicgen_engine["label"] == "MusicGen (Self-Hosted)"
        assert musicgen_engine["engine_type"] == "external_http"
        assert musicgen_engine["available"] is True


def test_musicgen_config_when_base_url_not_set():
    """Test MusicGen engine does not appear when BASE_URL is not set."""
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

        # Get config
        response = client.get("/api/config/")
        assert response.status_code == 200

        data = response.json()
        engines = data["features"]["instrumental_engines"]

        # MusicGen should not be in the list
        musicgen_engines = [e for e in engines if e["name"] == "musicgen"]
        assert len(musicgen_engines) == 0


def test_musicgen_engine_factory():
    """Test that engine factory can create MusicGen external engine."""
    from app.services.instrumental_engine import get_instrumental_engine
    from app.core.config import Settings

    # Create mock settings with MusicGen configured
    with patch("app.services.instrumental_engine.settings") as mock_settings:
        mock_settings.get_engine_config = Mock(return_value=InstrumentalEngineConfig(
            name="musicgen",
            label="MusicGen (Self-Hosted)",
            engine_type="external_http",
            base_url="https://musicgen.example.com",
            api_key=None,
            model="facebook/musicgen-medium",
        ))

        # Create engine
        engine = get_instrumental_engine(
            engine_type="external_http",
            model="musicgen",
            settings=mock_settings
        )

        # Verify engine was created
        assert engine is not None
        assert hasattr(engine, "engine_config")
        assert engine.engine_config.name == "musicgen"
        assert engine.engine_config.base_url == "https://musicgen.example.com"
        assert engine.engine_config.model == "facebook/musicgen-medium"


def test_musicgen_uses_v1_endpoint():
    """Test that MusicGen uses /v1/generate/audio endpoint."""
    from app.services.instrumental_engine import ExternalInstrumentalEngine
    from app.core.config import InstrumentalEngineConfig

    # Create MusicGen engine config
    engine_config = InstrumentalEngineConfig(
        name="musicgen",
        label="MusicGen (Self-Hosted)",
        engine_type="external_http",
        base_url="https://musicgen.example.com",
        api_key=None,
        model="facebook/musicgen-medium",
    )

    engine = ExternalInstrumentalEngine(engine_config=engine_config)

    # Mock httpx.post to capture the URL
    with patch("app.services.instrumental_engine.httpx.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ready",
            "audio_url": "https://cdn.example.com/music.wav"
        }
        mock_post.return_value = mock_response

        # Call the generic HTTP generate method
        try:
            engine._generic_http_generate("test prompt", 30)
        except Exception:
            pass  # We don't care about errors, just want to check the URL

        # Verify the URL used the /v1/ endpoint for MusicGen
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://musicgen.example.com/v1/generate/audio"


def test_musicgen_request_payload():
    """Test that MusicGen sends correct request payload."""
    from app.services.instrumental_engine import ExternalInstrumentalEngine
    from app.core.config import InstrumentalEngineConfig

    engine_config = InstrumentalEngineConfig(
        name="musicgen",
        label="MusicGen (Self-Hosted)",
        engine_type="external_http",
        base_url="https://musicgen.example.com",
        api_key=None,
        model="facebook/musicgen-medium",
    )

    engine = ExternalInstrumentalEngine(engine_config=engine_config)

    with patch("app.services.instrumental_engine.httpx.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ready",
            "audio_url": "https://cdn.example.com/music.wav"
        }
        mock_post.return_value = mock_response

        # Generate audio
        try:
            engine._generic_http_generate("energetic pop track", 30)
        except Exception:
            pass

        # Verify request payload
        call_args = mock_post.call_args
        assert "json" in call_args[1]
        payload = call_args[1]["json"]
        assert payload["model"] == "facebook/musicgen-medium"
        assert payload["prompt"] == "energetic pop track"
        assert payload["seconds_total"] == 30

        # Verify no API key header for MusicGen (self-hosted, no auth)
        headers = call_args[1]["headers"]
        assert "Authorization" not in headers
