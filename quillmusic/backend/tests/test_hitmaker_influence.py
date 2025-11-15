"""
Tests for HitMaker influence blending functionality.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_influence_blueprint_basic():
    """Test applying influences to a blueprint."""
    # Create a blueprint first
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "Upbeat pop song",
            "genre": "pop",
            "mood": "happy",
            "duration_seconds": 180,
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Apply influences
    response = client.post(
        "/api/hitmaker/influence/blueprint",
        json={
            "source_blueprint_id": blueprint_id,
            "influences": [
                {"name": "The Weeknd", "weight": 0.7},
                {"name": "Billie Eilish", "weight": 0.3},
            ],
            "target_mood": "dark",
            "target_genre": "r&b",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "adjusted_dna" in data
    assert "hook_suggestions" in data
    assert "chorus_rewrite_ideas" in data
    assert "structure_suggestions" in data
    assert "instrumentation_ideas" in data
    assert "vocal_style_notes" in data

    # Verify adjusted DNA
    adjusted_dna = data["adjusted_dna"]
    assert adjusted_dna["dominant_mood"] == "dark"
    assert adjusted_dna["genre_guess"] == "r&b"

    # Verify suggestions are non-empty
    assert len(data["hook_suggestions"]) > 0
    assert len(data["chorus_rewrite_ideas"]) > 0
    assert len(data["structure_suggestions"]) > 0
    assert len(data["instrumentation_ideas"]) > 0
    assert len(data["vocal_style_notes"]) > 0


def test_influence_manual_project_basic():
    """Test applying influences to a manual project."""
    # Create a manual project
    project_response = client.post(
        "/api/manual/projects",
        json={
            "name": "Test Track",
            "tempo_bpm": 120,
            "key": "C",
            "time_signature": "4/4",
        },
    )
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]

    # Apply influences
    response = client.post(
        "/api/hitmaker/influence/manual",
        json={
            "source_manual_project_id": project_id,
            "influences": [
                {"name": "Drake", "weight": 0.8},
            ],
            "target_mood": "introspective",
            "target_genre": "hiphop",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "adjusted_dna" in data
    assert "hook_suggestions" in data

    # Verify suggestions
    assert len(data["hook_suggestions"]) > 0
    assert len(data["chorus_rewrite_ideas"]) > 0


def test_influence_weight_validation():
    """Test that influence weights are validated."""
    # Create blueprint
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "A neutral pop song for testing",
            "genre": "pop",
            "mood": "neutral",
            "duration_seconds": 180,
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Try to apply influences with total weight > 1.2
    response = client.post(
        "/api/hitmaker/influence/blueprint",
        json={
            "source_blueprint_id": blueprint_id,
            "influences": [
                {"name": "Artist A", "weight": 0.8},
                {"name": "Artist B", "weight": 0.6},  # Total = 1.4, too high
            ],
        },
    )

    assert response.status_code == 400
    assert "weight" in response.json()["detail"].lower()


def test_influence_blueprint_not_found():
    """Test influence with non-existent blueprint."""
    response = client.post(
        "/api/hitmaker/influence/blueprint",
        json={
            "source_blueprint_id": "nonexistent",
            "influences": [{"name": "Someone", "weight": 0.5}],
        },
    )

    assert response.status_code == 404


def test_influence_manual_not_found():
    """Test influence with non-existent manual project."""
    response = client.post(
        "/api/hitmaker/influence/manual",
        json={
            "source_manual_project_id": "nonexistent",
            "influences": [{"name": "Someone", "weight": 0.5}],
        },
    )

    assert response.status_code == 404


def test_influence_missing_source_id():
    """Test that source ID is required."""
    response = client.post(
        "/api/hitmaker/influence/blueprint",
        json={
            "influences": [{"name": "Someone", "weight": 0.5}],
        },
    )

    assert response.status_code == 400
