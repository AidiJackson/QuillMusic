"""
Tests for song blueprint generation
"""


def test_create_song_blueprint(client):
    """Test creating a song blueprint."""
    request_data = {
        "prompt": "A dreamy song about late night drives through the city",
        "genre": "Lo-fi",
        "mood": "Chill",
        "bpm": 85,
        "key": "Am",
        "duration_seconds": 180,
    }

    response = client.post("/api/song/blueprint", json=request_data)
    assert response.status_code == 200

    data = response.json()

    # Check basic fields
    assert "song_id" in data
    assert data["song_id"].startswith("song_")
    assert "title" in data
    assert len(data["title"]) > 0

    # Check genre and mood match request
    assert data["genre"] == request_data["genre"]
    assert data["mood"] == request_data["mood"]

    # Check BPM and key
    assert data["bpm"] == request_data["bpm"]
    assert data["key"] == request_data["key"]

    # Check sections
    assert "sections" in data
    assert len(data["sections"]) >= 3
    for section in data["sections"]:
        assert "id" in section
        assert "type" in section
        assert "name" in section
        assert "bars" in section
        assert "mood" in section
        assert "description" in section
        assert "instruments" in section

    # Check lyrics
    assert "lyrics" in data
    assert len(data["lyrics"]) > 0
    # Lyrics keys should match section IDs
    section_ids = {s["id"] for s in data["sections"]}
    lyrics_keys = set(data["lyrics"].keys())
    assert lyrics_keys == section_ids

    # Check vocal style
    assert "vocal_style" in data
    assert "gender" in data["vocal_style"]
    assert "tone" in data["vocal_style"]
    assert "energy" in data["vocal_style"]

    # Check notes
    assert "notes" in data


def test_create_song_blueprint_minimal(client):
    """Test creating a song blueprint with minimal required fields."""
    request_data = {
        "prompt": "An uplifting electronic dance track",
        "genre": "EDM",
        "mood": "Energetic",
    }

    response = client.post("/api/song/blueprint", json=request_data)
    assert response.status_code == 200

    data = response.json()

    # Should have defaults filled in
    assert "bpm" in data
    assert data["bpm"] > 0
    assert "key" in data
    assert len(data["key"]) > 0


def test_create_song_blueprint_invalid_prompt(client):
    """Test that short prompts are rejected."""
    request_data = {
        "prompt": "short",  # Too short
        "genre": "Pop",
        "mood": "Uplifting",
    }

    response = client.post("/api/song/blueprint", json=request_data)
    assert response.status_code == 422  # Validation error


def test_create_song_blueprint_different_genres(client):
    """Test blueprint generation for different genres."""
    genres = ["Pop", "Hip Hop", "EDM", "Rock", "Ambient"]

    for genre in genres:
        request_data = {
            "prompt": f"A great {genre} song with lots of energy",
            "genre": genre,
            "mood": "Energetic",
        }

        response = client.post("/api/song/blueprint", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["genre"] == genre
        assert len(data["sections"]) > 0
