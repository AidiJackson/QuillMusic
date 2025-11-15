"""
Tests for external instrumental engine with HTTP audio provider
"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_external_engine_config_error_missing_provider():
    """Test external engine fails when AUDIO_PROVIDER is not set to stable_audio_http."""
    # Create a blueprint first
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "An energetic EDM track",
            "genre": "EDM",
            "mood": "Energetic",
            "bpm": 128,
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Mock settings to have wrong provider
    with patch("app.services.instrumental_render_service.settings") as mock_settings:
        mock_settings.AUDIO_PROVIDER = "fake"
        mock_settings.AUDIO_API_BASE_URL = "https://api.example.com"
        mock_settings.AUDIO_API_KEY = "test-key"

        # Try to render with external_http engine
        render_response = client.post(
            "/api/instrumental/render",
            json={
                "source_type": "blueprint",
                "source_id": blueprint_id,
                "engine_type": "external_http",
            },
        )

        # Should still return 200 but job status should be "failed"
        assert render_response.status_code == 200
        data = render_response.json()
        assert data["status"] == "failed"
        assert "Configuration error" in data["error_message"]
        assert "AUDIO_PROVIDER" in data["error_message"]


def test_external_engine_config_error_missing_base_url():
    """Test external engine fails when AUDIO_API_BASE_URL is missing."""
    # Create a blueprint first
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "A chill lo-fi beat",
            "genre": "Lo-fi",
            "mood": "Chill",
            "bpm": 85,
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Mock settings with missing base URL
    with patch("app.services.instrumental_render_service.settings") as mock_settings:
        mock_settings.AUDIO_PROVIDER = "stable_audio_http"
        mock_settings.AUDIO_API_BASE_URL = None
        mock_settings.AUDIO_API_KEY = "test-key"

        # Try to render with external_http engine
        render_response = client.post(
            "/api/instrumental/render",
            json={
                "source_type": "blueprint",
                "source_id": blueprint_id,
                "engine_type": "external_http",
            },
        )

        assert render_response.status_code == 200
        data = render_response.json()
        assert data["status"] == "failed"
        assert "Configuration error" in data["error_message"]
        assert "AUDIO_API_BASE_URL" in data["error_message"]


def test_external_engine_config_error_missing_api_key():
    """Test external engine fails when AUDIO_API_KEY is missing."""
    # Create a blueprint first
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "A rock anthem",
            "genre": "Rock",
            "mood": "Energetic",
            "bpm": 120,
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Mock settings with missing API key
    with patch("app.services.instrumental_render_service.settings") as mock_settings:
        mock_settings.AUDIO_PROVIDER = "stable_audio_http"
        mock_settings.AUDIO_API_BASE_URL = "https://api.example.com"
        mock_settings.AUDIO_API_KEY = None

        # Try to render with external_http engine
        render_response = client.post(
            "/api/instrumental/render",
            json={
                "source_type": "blueprint",
                "source_id": blueprint_id,
                "engine_type": "external_http",
            },
        )

        assert render_response.status_code == 200
        data = render_response.json()
        assert data["status"] == "failed"
        assert "Configuration error" in data["error_message"]
        assert "AUDIO_API_KEY" in data["error_message"]


@patch("app.services.instrumental_engine.httpx.post")
def test_external_engine_success_blueprint(mock_post):
    """Test successful external engine rendering from blueprint."""
    # Mock successful HTTP response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "job-123",
        "status": "ready",
        "audio_url": "https://cdn.example.com/audio/job-123.mp3",
    }
    mock_post.return_value = mock_response

    # Create a blueprint
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "An upbeat pop song",
            "genre": "Pop",
            "mood": "Happy",
            "bpm": 120,
            "key": "C",
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Mock settings with valid configuration
    with patch("app.services.instrumental_render_service.settings") as mock_settings:
        mock_settings.AUDIO_PROVIDER = "stable_audio_http"
        mock_settings.AUDIO_API_BASE_URL = "https://api.example.com"
        mock_settings.AUDIO_API_KEY = "test-api-key"

        # Render with external_http engine
        render_response = client.post(
            "/api/instrumental/render",
            json={
                "source_type": "blueprint",
                "source_id": blueprint_id,
                "engine_type": "external_http",
            },
        )

        assert render_response.status_code == 200
        data = render_response.json()
        assert data["status"] == "ready"
        assert data["audio_url"] == "https://cdn.example.com/audio/job-123.mp3"
        assert data["duration_seconds"] > 0
        assert data["error_message"] is None

        # Verify HTTP call was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.example.com/v2/generate/audio"
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-api-key"
        assert "prompt" in call_args[1]["json"]
        assert "seconds_total" in call_args[1]["json"]


@patch("app.services.instrumental_engine.httpx.post")
def test_external_engine_success_manual_project(mock_post):
    """Test successful external engine rendering from manual project."""
    # Mock successful HTTP response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "job-456",
        "status": "ready",
        "audio_url": "https://cdn.example.com/audio/job-456.mp3",
    }
    mock_post.return_value = mock_response

    # Create a manual project
    project_response = client.post(
        "/api/manual/projects",
        json={
            "name": "Test Project",
            "tempo_bpm": 128,
            "time_signature": "4/4",
            "key": "Am",
        },
    )
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]

    # Mock settings with valid configuration
    with patch("app.services.instrumental_render_service.settings") as mock_settings:
        mock_settings.AUDIO_PROVIDER = "stable_audio_http"
        mock_settings.AUDIO_API_BASE_URL = "https://api.example.com"
        mock_settings.AUDIO_API_KEY = "test-api-key"

        # Render with external_http engine
        render_response = client.post(
            "/api/instrumental/render",
            json={
                "source_type": "manual_project",
                "source_id": project_id,
                "engine_type": "external_http",
            },
        )

        assert render_response.status_code == 200
        data = render_response.json()
        assert data["status"] == "ready"
        assert data["audio_url"] == "https://cdn.example.com/audio/job-456.mp3"
        assert data["duration_seconds"] > 0
        assert data["error_message"] is None


@patch("app.services.instrumental_engine.httpx.post")
def test_external_engine_failure_http_error(mock_post):
    """Test external engine handles HTTP errors gracefully."""
    # Mock HTTP error response
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    mock_post.return_value = mock_response

    # Create a blueprint
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "A jazz tune",
            "genre": "Jazz",
            "mood": "Relaxed",
            "bpm": 100,
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Mock settings with valid configuration
    with patch("app.services.instrumental_render_service.settings") as mock_settings:
        mock_settings.AUDIO_PROVIDER = "stable_audio_http"
        mock_settings.AUDIO_API_BASE_URL = "https://api.example.com"
        mock_settings.AUDIO_API_KEY = "test-api-key"

        # Try to render with external_http engine
        render_response = client.post(
            "/api/instrumental/render",
            json={
                "source_type": "blueprint",
                "source_id": blueprint_id,
                "engine_type": "external_http",
            },
        )

        assert render_response.status_code == 200
        data = render_response.json()
        assert data["status"] == "failed"
        assert "Audio provider error" in data["error_message"]


@patch("app.services.instrumental_engine.httpx.post")
def test_external_engine_failure_invalid_response(mock_post):
    """Test external engine handles invalid API responses."""
    # Mock response with unexpected format
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "job-789",
        "status": "pending",  # Not "ready"
        # Missing audio_url
    }
    mock_post.return_value = mock_response

    # Create a blueprint
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "A classical piece",
            "genre": "Classical",
            "mood": "Elegant",
            "bpm": 90,
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Mock settings with valid configuration
    with patch("app.services.instrumental_render_service.settings") as mock_settings:
        mock_settings.AUDIO_PROVIDER = "stable_audio_http"
        mock_settings.AUDIO_API_BASE_URL = "https://api.example.com"
        mock_settings.AUDIO_API_KEY = "test-api-key"

        # Try to render with external_http engine
        render_response = client.post(
            "/api/instrumental/render",
            json={
                "source_type": "blueprint",
                "source_id": blueprint_id,
                "engine_type": "external_http",
            },
        )

        assert render_response.status_code == 200
        data = render_response.json()
        assert data["status"] == "failed"
        assert "Audio provider error" in data["error_message"]


@patch("app.services.instrumental_engine.httpx.post")
def test_external_engine_failure_network_exception(mock_post):
    """Test external engine handles network exceptions."""
    # Mock network exception
    import httpx
    mock_post.side_effect = httpx.ConnectError("Connection refused")

    # Create a blueprint
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "A reggae track",
            "genre": "Reggae",
            "mood": "Laid-back",
            "bpm": 95,
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Mock settings with valid configuration
    with patch("app.services.instrumental_render_service.settings") as mock_settings:
        mock_settings.AUDIO_PROVIDER = "stable_audio_http"
        mock_settings.AUDIO_API_BASE_URL = "https://api.example.com"
        mock_settings.AUDIO_API_KEY = "test-api-key"

        # Try to render with external_http engine
        render_response = client.post(
            "/api/instrumental/render",
            json={
                "source_type": "blueprint",
                "source_id": blueprint_id,
                "engine_type": "external_http",
            },
        )

        assert render_response.status_code == 200
        data = render_response.json()
        assert data["status"] == "failed"
        assert "Audio provider error" in data["error_message"]
