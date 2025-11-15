"""
Tests for HitMaker analysis of Manual Creator projects.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_manual_project_basic():
    """Test basic manual project analysis."""
    # Create a sample project
    project_response = client.post(
        "/api/manual/projects",
        json={
            "name": "Test Song",
            "tempo_bpm": 120,
            "key": "C",
            "time_signature": "4/4",
        },
    )
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]

    # Add some tracks and patterns
    # Add drums track
    drums_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={
            "instrument_type": "drums",
            "name": "Drums",
            "channel_index": 0,
            
        },
    )
    assert drums_response.status_code == 200
    drums_id = drums_response.json()["id"]

    # Add a pattern
    pattern_response = client.post(
        f"/api/manual/tracks/{drums_id}/patterns",
        json={
            "name": "Pattern 1",
            "start_bar": 0,
            "length_bars": 4,
        },
    )
    assert pattern_response.status_code == 200
    pattern_id = pattern_response.json()["id"]

    # Add some notes
    notes_response = client.post(
        f"/api/manual/patterns/{pattern_id}/notes/bulk",
        json=[
            {"pattern_id": pattern_id, "step_index": 0, "pitch": 36, "velocity": 80},
            {"pattern_id": pattern_id, "step_index": 4, "pitch": 38, "velocity": 80},
            {"pattern_id": pattern_id, "step_index": 8, "pitch": 36, "velocity": 80},
            {"pattern_id": pattern_id, "step_index": 12, "pitch": 38, "velocity": 80},
        ],
    )
    assert notes_response.status_code == 200

    # Call analyze endpoint
    response = client.post(
        "/api/hitmaker/analyze/manual",
        params={"manual_project_id": project_id},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "dna" in data
    assert "score" in data
    assert "commentary" in data
    assert "risks" in data
    assert "opportunities" in data

    # Verify DNA
    dna = data["dna"]
    assert dna["manual_project_id"] == project_id
    assert dna["blueprint_id"] is None
    assert len(dna["sections"]) > 0
    assert len(dna["global_energy_curve"]) > 0
    assert len(dna["global_tension_curve"]) > 0

    # Verify score breakdown
    score = data["score"]
    assert 0 <= score["overall"] <= 100
    assert 0 <= score["hook_strength"] <= 100
    assert 0 <= score["structure"] <= 100


def test_analyze_empty_manual_project():
    """Test analyzing an empty manual project."""
    # Create project with no tracks/patterns
    project_response = client.post(
        "/api/manual/projects",
        json={
            "name": "Empty Project",
            "tempo_bpm": 100,
            "key": "C",
            "time_signature": "4/4",
        },
    )
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]

    # Analyze
    response = client.post(
        "/api/hitmaker/analyze/manual",
        params={"manual_project_id": project_id},
    )

    assert response.status_code == 200
    data = response.json()

    # Should still return valid analysis
    assert "dna" in data
    assert "score" in data

    # Score should be lower for empty project
    score = data["score"]
    assert score["overall"] < 70  # Empty projects should score lower


def test_analyze_manual_not_found():
    """Test analyzing non-existent project."""
    response = client.post(
        "/api/hitmaker/analyze/manual",
        params={"manual_project_id": "nonexistent-id"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_manual_genre_inference():
    """Test genre inference from BPM and track types."""
    # Create EDM-style project (high BPM with drums)
    project_response = client.post(
        "/api/manual/projects",
        json={
            "name": "EDM Track",
            "tempo_bpm": 140,
            "key": "A",
            "time_signature": "4/4",
        },
    )
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]

    # Add drums
    drums_response = client.post(
        f"/api/manual/projects/{project_id}/tracks",
        json={
            "instrument_type": "drums",
            "name": "Drums",
            "channel_index": 0,
            
        },
    )
    assert drums_response.status_code == 200
    drums_id = drums_response.json()["id"]

    # Add pattern
    pattern_response = client.post(
        f"/api/manual/tracks/{drums_id}/patterns",
        json={
            "name": "Pattern 1",
            "start_bar": 0,
            "length_bars": 4,
        },
    )
    assert pattern_response.status_code == 200
    pattern_id = pattern_response.json()["id"]

    # Add notes (dense pattern)
    notes = [{"pattern_id": pattern_id, "step_index": i, "pitch": 36, "velocity": 90} for i in range(16)]
    notes_response = client.post(
        f"/api/manual/patterns/{pattern_id}/notes/bulk",
        json=notes,
    )
    assert notes_response.status_code == 200

    # Analyze
    response = client.post(
        "/api/hitmaker/analyze/manual",
        params={"manual_project_id": project_id},
    )

    assert response.status_code == 200
    data = response.json()

    # Should infer EDM or similar high-energy genre
    genre_guess = data["dna"]["genre_guess"]
    assert genre_guess in ["edm", "house", "dubstep", "trap", "pop"]
