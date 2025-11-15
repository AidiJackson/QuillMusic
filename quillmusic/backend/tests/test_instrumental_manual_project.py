"""
Tests for instrumental rendering from manual projects
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_render_instrumental_from_manual_project():
    """Test rendering an instrumental from a manual project."""
    # Create a manual project
    project_response = client.post(
        "/api/manual/projects",
        json={
            "name": "Test Manual Project",
            "tempo_bpm": 120,
            "time_signature": "4/4",
            "key": "C",
        },
    )
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]

    # Add a track
    track_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={
            "name": "Drums",
            "instrument_type": "drums",
            "channel_index": 0,
        },
    )
    assert track_response.status_code == 200
    track_id = track_response.json()["id"]

    # Add a pattern
    pattern_response = client.post(
        f"/api/manual/tracks/{track_id}/patterns",
        json={
            "name": "Drum Pattern 1",
            "length_bars": 4,
            "start_bar": 0,
        },
    )
    assert pattern_response.status_code == 200
    pattern_id = pattern_response.json()["id"]

    # Add some notes
    notes_response = client.post(
        f"/api/manual/patterns/{pattern_id}/notes/bulk",
        json=[
            {"pattern_id": pattern_id, "step_index": 0, "pitch": 36, "velocity": 100},
            {"pattern_id": pattern_id, "step_index": 4, "pitch": 38, "velocity": 90},
            {"pattern_id": pattern_id, "step_index": 8, "pitch": 36, "velocity": 100},
        ],
    )
    assert notes_response.status_code == 200

    # Now render instrumental from the manual project
    render_response = client.post(
        "/api/instrumental/render",
        json={
            "source_type": "manual_project",
            "source_id": project_id,
            "engine_type": "fake",
        },
    )
    assert render_response.status_code == 200

    data = render_response.json()
    assert data["status"] == "ready"
    assert data["engine_type"] == "fake"
    assert data["source_type"] == "manual_project"
    assert data["source_id"] == project_id
    assert data["audio_url"] is not None
    assert data["audio_url"].startswith("/audio/fake-instrumental/manual-")
    assert data["duration_seconds"] is not None
    assert data["duration_seconds"] > 0


def test_render_instrumental_from_empty_manual_project():
    """Test rendering from a manual project with no tracks/patterns."""
    # Create a manual project with no tracks
    project_response = client.post(
        "/api/manual/projects",
        json={
            "name": "Empty Project",
            "tempo_bpm": 90,
            "time_signature": "4/4",
        },
    )
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]

    # Render instrumental (should use default duration)
    render_response = client.post(
        "/api/instrumental/render",
        json={
            "source_type": "manual_project",
            "source_id": project_id,
            "engine_type": "fake",
        },
    )
    assert render_response.status_code == 200

    data = render_response.json()
    assert data["status"] == "ready"
    # Should have default duration based on 16 bars at 90 BPM
    assert data["duration_seconds"] > 0


def test_render_instrumental_with_multiple_tracks():
    """Test rendering from a project with multiple tracks and patterns."""
    # Create project
    project_response = client.post(
        "/api/manual/projects",
        json={
            "name": "Multi-track Project",
            "tempo_bpm": 128,
            "time_signature": "4/4",
            "key": "Am",
        },
    )
    project_id = project_response.json()["id"]

    # Add drums track with pattern
    drums_track_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={"name": "Drums", "instrument_type": "drums", "channel_index": 0},
    )
    drums_track_id = drums_track_response.json()["id"]

    client.post(
        f"/api/manual/tracks/{drums_track_id}/patterns",
        json={"name": "Drums 1", "length_bars": 8, "start_bar": 0},
    )

    # Add bass track with pattern
    bass_track_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={"name": "Bass", "instrument_type": "bass", "channel_index": 1},
    )
    bass_track_id = bass_track_response.json()["id"]

    client.post(
        f"/api/manual/tracks/{bass_track_id}/patterns",
        json={"name": "Bass 1", "length_bars": 4, "start_bar": 8},
    )

    # Render instrumental
    render_response = client.post(
        "/api/instrumental/render",
        json={
            "source_type": "manual_project",
            "source_id": project_id,
            "engine_type": "fake",
        },
    )
    assert render_response.status_code == 200

    data = render_response.json()
    assert data["status"] == "ready"
    # Duration should be based on last pattern end (bar 12)
    assert data["duration_seconds"] > 0


def test_render_instrumental_invalid_manual_project():
    """Test rendering with non-existent manual project ID."""
    render_response = client.post(
        "/api/instrumental/render",
        json={
            "source_type": "manual_project",
            "source_id": "non-existent-project",
            "engine_type": "fake",
        },
    )
    # Should return 200 with failed status instead of 404
    assert render_response.status_code == 200
    data = render_response.json()
    assert data["status"] == "failed"
    assert "not found" in data["error_message"].lower()


def test_render_instrumental_with_style_hint():
    """Test rendering with style hint and quality parameters."""
    # Create project
    project_response = client.post(
        "/api/manual/projects",
        json={
            "name": "Styled Project",
            "tempo_bpm": 110,
            "time_signature": "4/4",
        },
    )
    project_id = project_response.json()["id"]

    # Render with style parameters
    render_response = client.post(
        "/api/instrumental/render",
        json={
            "source_type": "manual_project",
            "source_id": project_id,
            "engine_type": "fake",
            "style_hint": "dark cinematic trap with atmospheric pads",
            "quality": "high",
        },
    )
    assert render_response.status_code == 200

    data = render_response.json()
    assert data["status"] == "ready"
    # Style hint and quality are accepted but may not affect fake engine
