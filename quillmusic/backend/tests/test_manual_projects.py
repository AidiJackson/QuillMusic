"""
Tests for Manual Creator API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_project():
    """Test creating a manual project."""
    response = client.post(
        "/api/manual/projects",
        json={
            "name": "Test Project",
            "tempo_bpm": 120,
            "time_signature": "4/4",
            "key": "C",
            "description": "A test project",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["tempo_bpm"] == 120
    assert data["time_signature"] == "4/4"
    assert data["key"] == "C"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_list_projects():
    """Test listing projects."""
    # Create a project first
    create_response = client.post(
        "/api/manual/projects",
        json={
            "name": "List Test Project",
            "tempo_bpm": 130,
            "time_signature": "4/4",
        },
    )
    assert create_response.status_code == 200

    # List projects
    response = client.get("/api/manual/projects")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_create_track():
    """Test creating a track for a project."""
    # Create project first
    project_response = client.post(
        "/api/manual/projects",
        json={
            "name": "Track Test Project",
            "tempo_bpm": 120,
            "time_signature": "4/4",
        },
    )
    project_id = project_response.json()["id"]

    # Create track
    response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={
            "name": "Drums",
            "instrument_type": "drums",
            "channel_index": 0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Drums"
    assert data["instrument_type"] == "drums"
    assert data["channel_index"] == 0
    assert data["project_id"] == project_id
    assert data["volume"] == 0.8  # default
    assert data["pan"] == 0.0  # default
    assert data["muted"] is False
    assert data["solo"] is False


def test_update_track():
    """Test updating track properties."""
    # Create project and track
    project_response = client.post(
        "/api/manual/projects",
        json={"name": "Update Track Test", "tempo_bpm": 120, "time_signature": "4/4"},
    )
    project_id = project_response.json()["id"]

    track_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={"name": "Bass", "instrument_type": "bass", "channel_index": 1},
    )
    track_id = track_response.json()["id"]

    # Update track
    response = client.patch(
        f"/api/manual/tracks/{track_id}",
        json={
            "volume": 0.6,
            "pan": -0.5,
            "muted": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["volume"] == 0.6
    assert data["pan"] == -0.5
    assert data["muted"] is True


def test_create_pattern():
    """Test creating a pattern for a track."""
    # Create project and track
    project_response = client.post(
        "/api/manual/projects",
        json={"name": "Pattern Test", "tempo_bpm": 120, "time_signature": "4/4"},
    )
    project_id = project_response.json()["id"]

    track_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={"name": "Lead", "instrument_type": "lead", "channel_index": 0},
    )
    track_id = track_response.json()["id"]

    # Create pattern
    response = client.post(
        f"/api/manual/tracks/{track_id}/patterns",
        json={
            "name": "Pattern 1",
            "length_bars": 4,
            "start_bar": 0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Pattern 1"
    assert data["length_bars"] == 4
    assert data["start_bar"] == 0
    assert data["track_id"] == track_id


def test_update_pattern():
    """Test updating pattern properties."""
    # Create project, track, and pattern
    project_response = client.post(
        "/api/manual/projects",
        json={"name": "Update Pattern Test", "tempo_bpm": 120, "time_signature": "4/4"},
    )
    project_id = project_response.json()["id"]

    track_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={"name": "Chords", "instrument_type": "chords", "channel_index": 0},
    )
    track_id = track_response.json()["id"]

    pattern_response = client.post(
        f"/api/manual/tracks/{track_id}/patterns",
        json={"name": "Pattern A", "length_bars": 2, "start_bar": 0},
    )
    pattern_id = pattern_response.json()["id"]

    # Update pattern
    response = client.patch(
        f"/api/manual/patterns/{pattern_id}",
        json={
            "name": "Pattern A Updated",
            "length_bars": 8,
            "start_bar": 4,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Pattern A Updated"
    assert data["length_bars"] == 8
    assert data["start_bar"] == 4


def test_bulk_replace_notes():
    """Test bulk replacing notes for a pattern."""
    # Create project, track, and pattern
    project_response = client.post(
        "/api/manual/projects",
        json={"name": "Notes Test", "tempo_bpm": 120, "time_signature": "4/4"},
    )
    project_id = project_response.json()["id"]

    track_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={"name": "Melody", "instrument_type": "lead", "channel_index": 0},
    )
    track_id = track_response.json()["id"]

    pattern_response = client.post(
        f"/api/manual/tracks/{track_id}/patterns",
        json={"name": "Melody Pattern", "length_bars": 2, "start_bar": 0},
    )
    pattern_id = pattern_response.json()["id"]

    # Add notes
    notes = [
        {"pattern_id": pattern_id, "step_index": 0, "pitch": 60, "velocity": 100},
        {"pattern_id": pattern_id, "step_index": 4, "pitch": 64, "velocity": 80},
        {"pattern_id": pattern_id, "step_index": 8, "pitch": 67, "velocity": 90},
    ]

    response = client.post(
        f"/api/manual/patterns/{pattern_id}/notes/bulk",
        json=notes,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["pitch"] == 60
    assert data[1]["pitch"] == 64
    assert data[2]["pitch"] == 67


def test_get_pattern_notes():
    """Test retrieving notes for a pattern."""
    # Create project, track, pattern, and notes
    project_response = client.post(
        "/api/manual/projects",
        json={"name": "Get Notes Test", "tempo_bpm": 120, "time_signature": "4/4"},
    )
    project_id = project_response.json()["id"]

    track_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={"name": "Test Track", "instrument_type": "drums", "channel_index": 0},
    )
    track_id = track_response.json()["id"]

    pattern_response = client.post(
        f"/api/manual/tracks/{track_id}/patterns",
        json={"name": "Test Pattern", "length_bars": 1, "start_bar": 0},
    )
    pattern_id = pattern_response.json()["id"]

    # Add notes
    notes = [
        {"pattern_id": pattern_id, "step_index": 0, "pitch": 36, "velocity": 127},
        {"pattern_id": pattern_id, "step_index": 8, "pitch": 38, "velocity": 100},
    ]
    client.post(f"/api/manual/patterns/{pattern_id}/notes/bulk", json=notes)

    # Get notes
    response = client.get(f"/api/manual/patterns/{pattern_id}/notes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["pitch"] == 36
    assert data[1]["pitch"] == 38


def test_get_project_detail():
    """Test getting complete project detail with all related data."""
    # Create a project
    project_response = client.post(
        "/api/manual/projects",
        json={
            "name": "Full Project Test",
            "tempo_bpm": 128,
            "time_signature": "4/4",
            "key": "Am",
        },
    )
    project_id = project_response.json()["id"]

    # Create two tracks
    track1_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={"name": "Drums", "instrument_type": "drums", "channel_index": 0},
    )
    track1_id = track1_response.json()["id"]

    track2_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={"name": "Bass", "instrument_type": "bass", "channel_index": 1},
    )
    track2_id = track2_response.json()["id"]

    # Create patterns
    pattern1_response = client.post(
        f"/api/manual/tracks/{track1_id}/patterns",
        json={"name": "Drum Pattern 1", "length_bars": 2, "start_bar": 0},
    )
    pattern1_id = pattern1_response.json()["id"]

    pattern2_response = client.post(
        f"/api/manual/tracks/{track2_id}/patterns",
        json={"name": "Bass Pattern 1", "length_bars": 2, "start_bar": 0},
    )
    pattern2_id = pattern2_response.json()["id"]

    # Add notes to patterns
    client.post(
        f"/api/manual/patterns/{pattern1_id}/notes/bulk",
        json=[
            {"pattern_id": pattern1_id, "step_index": 0, "pitch": 36, "velocity": 100},
            {"pattern_id": pattern1_id, "step_index": 8, "pitch": 38, "velocity": 90},
        ],
    )

    client.post(
        f"/api/manual/patterns/{pattern2_id}/notes/bulk",
        json=[
            {"pattern_id": pattern2_id, "step_index": 0, "pitch": 40, "velocity": 110},
        ],
    )

    # Get project detail
    response = client.get(f"/api/manual/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "project" in data
    assert "tracks" in data
    assert "patterns" in data
    assert "notes" in data

    # Verify project
    assert data["project"]["id"] == project_id
    assert data["project"]["name"] == "Full Project Test"
    assert data["project"]["tempo_bpm"] == 128

    # Verify tracks
    assert len(data["tracks"]) == 2
    assert data["tracks"][0]["name"] == "Drums"
    assert data["tracks"][1]["name"] == "Bass"

    # Verify patterns
    assert len(data["patterns"]) == 2

    # Verify notes
    assert len(data["notes"]) == 3


def test_delete_project():
    """Test deleting a project cascades to all related data."""
    # Create project with tracks, patterns, and notes
    project_response = client.post(
        "/api/manual/projects",
        json={"name": "Delete Test", "tempo_bpm": 120, "time_signature": "4/4"},
    )
    project_id = project_response.json()["id"]

    track_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={"name": "Test Track", "instrument_type": "drums", "channel_index": 0},
    )
    track_id = track_response.json()["id"]

    pattern_response = client.post(
        f"/api/manual/tracks/{track_id}/patterns",
        json={"name": "Test Pattern", "length_bars": 2, "start_bar": 0},
    )
    pattern_id = pattern_response.json()["id"]

    # Delete project
    response = client.delete(f"/api/manual/projects/{project_id}")
    assert response.status_code == 200

    # Verify project is gone
    get_response = client.get(f"/api/manual/projects/{project_id}")
    assert get_response.status_code == 404


def test_delete_track():
    """Test deleting a track cascades to patterns and notes."""
    # Create project, track, and pattern
    project_response = client.post(
        "/api/manual/projects",
        json={"name": "Delete Track Test", "tempo_bpm": 120, "time_signature": "4/4"},
    )
    project_id = project_response.json()["id"]

    track_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={"name": "Track to Delete", "instrument_type": "bass", "channel_index": 0},
    )
    track_id = track_response.json()["id"]

    pattern_response = client.post(
        f"/api/manual/tracks/{track_id}/patterns",
        json={"name": "Pattern", "length_bars": 2, "start_bar": 0},
    )
    pattern_id = pattern_response.json()["id"]

    # Delete track
    response = client.delete(f"/api/manual/tracks/{track_id}")
    assert response.status_code == 200

    # Verify pattern is also gone
    get_pattern_response = client.get(f"/api/manual/patterns/{pattern_id}/notes")
    assert get_pattern_response.status_code == 404
