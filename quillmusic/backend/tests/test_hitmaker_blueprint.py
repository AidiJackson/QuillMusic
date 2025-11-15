"""
Tests for HitMaker analysis of AI-generated blueprints.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_blueprint_basic():
    """Test basic blueprint analysis."""
    # Create a sample blueprint first
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "Upbeat pop song about summer love",
            "genre": "pop",
            "mood": "happy",
            "duration_seconds": 180,
        },
    )
    assert blueprint_response.status_code == 200
    blueprint = blueprint_response.json()
    blueprint_id = blueprint["song_id"]

    # Call analyze endpoint
    response = client.post(
        "/api/hitmaker/analyze/blueprint",
        params={"blueprint_id": blueprint_id},
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
    assert dna["blueprint_id"] == blueprint_id
    assert dna["manual_project_id"] is None
    assert len(dna["sections"]) > 0
    assert len(dna["global_energy_curve"]) > 0
    assert len(dna["global_tension_curve"]) > 0
    assert "genre_guess" in dna
    assert "dominant_mood" in dna

    # Verify score breakdown
    score = data["score"]
    assert 0 <= score["overall"] <= 100
    assert 0 <= score["hook_strength"] <= 100
    assert 0 <= score["structure"] <= 100
    assert 0 <= score["lyrics_emotion"] <= 100
    assert 0 <= score["genre_fit"] <= 100
    assert 0 <= score["originality"] <= 100
    assert 0 <= score["replay_value"] <= 100

    # Verify insights
    assert isinstance(data["commentary"], list)
    assert len(data["commentary"]) > 0
    assert isinstance(data["risks"], list)
    assert isinstance(data["opportunities"], list)


def test_analyze_blueprint_section_energy():
    """Test that sections have different energy levels."""
    # Create a blueprint
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "Emotional ballad with powerful chorus",
            "genre": "ballad",
            "mood": "emotional",
            "duration_seconds": 240,
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Analyze
    response = client.post(
        "/api/hitmaker/analyze/blueprint",
        params={"blueprint_id": blueprint_id},
    )

    assert response.status_code == 200
    data = response.json()

    # Check that sections have valid energy/tension values
    sections = data["dna"]["sections"]
    assert len(sections) > 0
    for section in sections:
        assert 0.0 <= section["energy"] <= 1.0
        assert 0.0 <= section["tension"] <= 1.0
        assert 0.0 <= section["hook_density"] <= 1.0
        assert "name" in section
        assert "position_index" in section


def test_analyze_blueprint_not_found():
    """Test analyzing non-existent blueprint."""
    response = client.post(
        "/api/hitmaker/analyze/blueprint",
        params={"blueprint_id": "nonexistent-id"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_analyze_blueprint_structure_notes():
    """Test that structure notes are generated."""
    # Create a blueprint
    blueprint_response = client.post(
        "/api/song/blueprint",
        json={
            "prompt": "Catchy dance track with big drops",
            "genre": "edm",
            "mood": "energetic",
            "duration_seconds": 200,
        },
    )
    assert blueprint_response.status_code == 200
    blueprint_id = blueprint_response.json()["song_id"]

    # Analyze
    response = client.post(
        "/api/hitmaker/analyze/blueprint",
        params={"blueprint_id": blueprint_id},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure notes exist
    assert "structure_notes" in data["dna"]
    assert isinstance(data["dna"]["structure_notes"], list)


def test_hitscore_ranges_valid():
    """Test that HitScores are always in valid ranges."""
    # Create multiple blueprints with different characteristics
    for genre in ["pop", "rock", "hiphop"]:
        blueprint_response = client.post(
            "/api/song/blueprint",
            json={
                "prompt": f"A great {genre} song",
                "genre": genre,
                "mood": "energetic",
                "duration_seconds": 180,
            },
        )
        assert blueprint_response.status_code == 200
        blueprint_id = blueprint_response.json()["song_id"]

        # Analyze
        response = client.post(
            "/api/hitmaker/analyze/blueprint",
            params={"blueprint_id": blueprint_id},
        )

        assert response.status_code == 200
        score = response.json()["score"]

        # All scores should be 0-100
        for key, value in score.items():
            assert 0 <= value <= 100, f"{key} score {value} out of range for {genre}"
