"""
Tests for instrumental rendering from AI song blueprints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_render_instrumental_from_blueprint():
    """Test rendering an instrumental from a song blueprint."""
    # First, create a blueprint
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "An energetic EDM track with powerful drops",
            "genre": "EDM",
            "mood": "Energetic",
            "bpm": 128,
            "key": "Am",
        },
    )
    assert blueprint_response.status_code == 200
    blueprint = blueprint_response.json()
    blueprint_id = blueprint["song_id"]

    # Now render instrumental from the blueprint
    render_response = client.post(
        "/api/instrumental/render",
        json={
            "source_type": "blueprint",
            "source_id": blueprint_id,
            "engine_type": "fake",
        },
    )
    assert render_response.status_code == 200

    data = render_response.json()
    assert data["status"] == "ready"
    assert data["engine_type"] == "fake"
    assert data["source_type"] == "blueprint"
    assert data["source_id"] == blueprint_id
    assert data["audio_url"] is not None
    assert data["audio_url"].startswith("/audio/fake-instrumental/blueprint-")
    assert data["duration_seconds"] is not None
    assert data["duration_seconds"] > 0
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_render_instrumental_with_duration_override():
    """Test rendering with explicit duration override."""
    # Create a blueprint
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "A chill lo-fi hip hop beat",
            "genre": "Lo-fi",
            "mood": "Chill",
            "bpm": 85,
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Render with specific duration
    render_response = client.post(
        "/api/instrumental/render",
        json={
            "source_type": "blueprint",
            "source_id": blueprint_id,
            "engine_type": "fake",
            "duration_seconds": 180,  # 3 minutes
        },
    )
    assert render_response.status_code == 200

    data = render_response.json()
    assert data["status"] == "ready"
    assert data["duration_seconds"] == 180


def test_render_instrumental_with_external_http_engine():
    """Test rendering with external_http engine (should work via fake internally)."""
    # Create a blueprint
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "Dark ambient atmospheric track",
            "genre": "Ambient",
            "mood": "Dark",
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Render with external_http engine (delegates to fake for now)
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
    assert data["engine_type"] == "external_http"


def test_render_instrumental_invalid_blueprint():
    """Test rendering with non-existent blueprint ID."""
    render_response = client.post(
        "/api/instrumental/render",
        json={
            "source_type": "blueprint",
            "source_id": "non-existent-id",
            "engine_type": "fake",
        },
    )
    assert render_response.status_code == 404
    assert "not found" in render_response.json()["detail"].lower()


def test_get_instrumental_job_status():
    """Test retrieving job status by ID."""
    # Create blueprint and render
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "Upbeat pop song",
            "genre": "Pop",
            "mood": "Happy",
        },
    )
    blueprint_id = blueprint_response.json()["song_id"]

    render_response = client.post(
        "/api/instrumental/render",
        json={
            "source_type": "blueprint",
            "source_id": blueprint_id,
            "engine_type": "fake",
        },
    )
    job_id = render_response.json()["id"]

    # Get job status
    status_response = client.get(f"/api/instrumental/jobs/{job_id}")
    assert status_response.status_code == 200

    data = status_response.json()
    assert data["id"] == job_id
    assert data["status"] == "ready"
    assert data["audio_url"] is not None


def test_get_instrumental_job_not_found():
    """Test retrieving non-existent job."""
    status_response = client.get("/api/instrumental/jobs/non-existent-job-id")
    assert status_response.status_code == 404


def test_list_blueprints():
    """Test listing blueprints endpoint."""
    # Create a few blueprints
    for i in range(3):
        client.post(
            "/api/song/blueprint",
            json={
                "prompt": f"Test song {i}",
                "genre": "Test",
                "mood": "Test",
            },
        )

    # List blueprints
    list_response = client.get("/api/song/blueprints")
    assert list_response.status_code == 200

    data = list_response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_get_blueprint_by_id():
    """Test getting a specific blueprint by ID."""
    # Create a blueprint
    create_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "Specific test song",
            "genre": "Rock",
            "mood": "Energetic",
        },
    )
    blueprint_id = create_response.json()["song_id"]

    # Get blueprint by ID
    get_response = client.get(f"/api/song/blueprints/{blueprint_id}")
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["song_id"] == blueprint_id
    assert data["genre"] == "Rock"
    assert data["mood"] == "Energetic"
