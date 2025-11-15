"""
Tests for render job endpoints
"""


def test_create_render_job(client):
    """Test creating a render job."""
    request_data = {
        "song_id": "song_test123",
        "render_type": "full_mix",
    }

    response = client.post("/api/renders", json=request_data)
    assert response.status_code == 200

    data = response.json()

    # Check response structure
    assert "job_id" in data
    assert data["job_id"].startswith("job_")
    assert data["song_id"] == request_data["song_id"]
    assert data["render_type"] == request_data["render_type"]
    assert "status" in data
    assert data["status"] in ["queued", "processing", "ready", "failed"]

    # For fake engine, should be ready immediately
    assert data["status"] == "ready"

    # Should have audio URL
    assert "audio_url" in data
    assert data["audio_url"] is not None
    assert ".mp3" in data["audio_url"]

    # Should not have error
    assert data["error"] is None


def test_get_render_status(client):
    """Test getting render job status."""
    # First create a render job
    create_request = {
        "song_id": "song_test456",
        "render_type": "instrumental",
    }

    create_response = client.post("/api/renders", json=create_request)
    assert create_response.status_code == 200
    job_id = create_response.json()["job_id"]

    # Now get status
    status_response = client.get(f"/api/renders/{job_id}")
    assert status_response.status_code == 200

    data = status_response.json()
    assert data["job_id"] == job_id
    assert data["song_id"] == create_request["song_id"]
    assert data["render_type"] == create_request["render_type"]
    assert data["status"] == "ready"
    assert data["audio_url"] is not None


def test_get_render_status_unknown_job(client):
    """Test getting status for unknown job."""
    fake_job_id = "job_nonexistent"

    response = client.get(f"/api/renders/{fake_job_id}")
    assert response.status_code == 200  # Returns response, but with failed status

    data = response.json()
    assert data["status"] == "failed"
    assert data["error"] is not None


def test_create_render_job_different_types(client):
    """Test creating render jobs for different render types."""
    render_types = ["instrumental", "vocals", "full_mix"]

    for render_type in render_types:
        request_data = {
            "song_id": f"song_test_{render_type}",
            "render_type": render_type,
        }

        response = client.post("/api/renders", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["render_type"] == render_type
        assert data["status"] == "ready"
        assert render_type in data["audio_url"]


def test_create_render_job_invalid_type(client):
    """Test that invalid render types are rejected."""
    request_data = {
        "song_id": "song_test789",
        "render_type": "invalid_type",
    }

    response = client.post("/api/renders", json=request_data)
    assert response.status_code == 422  # Validation error
