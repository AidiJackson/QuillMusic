"""
Tests for LLM-based song blueprint engine
"""
import pytest
from app.schemas.song import SongBlueprintRequest
from app.services.song_blueprint_service import (
    FakeSongBlueprintEngine,
    LLMSongBlueprintEngine,
)
from app.services.llm_client import FakeLLMClient


def test_llm_engine_with_valid_response():
    """Test LLM engine with a valid mock response."""
    # Create a mock LLM response
    mock_response = {
        "title": "Electric Dreams",
        "sections": [
            {
                "id": "sec_intro",
                "type": "intro",
                "name": "Intro",
                "bars": 8,
                "mood": "Energetic",
                "description": "High-energy electronic intro",
                "instruments": ["synth", "drums"],
            },
            {
                "id": "sec_verse1",
                "type": "verse",
                "name": "Verse 1",
                "bars": 16,
                "mood": "Energetic",
                "description": "First verse with driving rhythm",
                "instruments": ["synth", "drums", "bass"],
            },
            {
                "id": "sec_chorus1",
                "type": "chorus",
                "name": "Chorus",
                "bars": 16,
                "mood": "Energetic",
                "description": "Explosive chorus",
                "instruments": ["synth", "drums", "bass", "lead"],
            },
        ],
        "lyrics": {
            "sec_intro": "[Instrumental]",
            "sec_verse1": "Running through the neon lights\nChasing electric dreams tonight",
            "sec_chorus1": "We're alive, we're electric\nFeel the pulse, so kinetic",
        },
        "vocal_style": {
            "gender": "female",
            "tone": "powerful",
            "energy": "high",
            "accent": None,
        },
        "notes": "Keep the energy high throughout. Use sidechain compression on bass.",
    }

    # Create fake LLM client with mock response
    fake_llm = FakeLLMClient(mock_response=mock_response)

    # Create LLM engine
    engine = LLMSongBlueprintEngine(llm_client=fake_llm)

    # Create request
    request = SongBlueprintRequest(
        prompt="An energetic EDM track about electric dreams",
        genre="EDM",
        mood="Energetic",
        bpm=128,
        key="Am",
    )

    # Generate blueprint
    blueprint = engine.generate_blueprint(request)

    # Assertions
    assert blueprint.title == "Electric Dreams"
    assert blueprint.genre == "EDM"
    assert blueprint.mood == "Energetic"
    assert blueprint.bpm == 128
    assert blueprint.key == "Am"
    assert len(blueprint.sections) == 3
    assert blueprint.sections[0].type == "intro"
    assert blueprint.sections[1].type == "verse"
    assert blueprint.sections[2].type == "chorus"
    assert "sec_verse1" in blueprint.lyrics
    assert "electric dreams" in blueprint.lyrics["sec_verse1"].lower()
    assert blueprint.vocal_style.gender == "female"
    assert blueprint.vocal_style.energy == "high"
    assert blueprint.notes is not None


def test_llm_engine_with_incomplete_response():
    """Test LLM engine gracefully handles incomplete responses."""
    # Create a mock LLM response with missing fields
    mock_response = {
        "title": "Incomplete Song",
        "sections": [
            {
                "id": "sec_verse1",
                "type": "verse",
                # Missing some fields - engine should use defaults
            }
        ],
        # Missing lyrics - engine should fill in
        # Missing vocal_style - engine should use defaults
    }

    fake_llm = FakeLLMClient(mock_response=mock_response)
    engine = LLMSongBlueprintEngine(llm_client=fake_llm)

    request = SongBlueprintRequest(
        prompt="A test song",
        genre="Pop",
        mood="Chill",
    )

    blueprint = engine.generate_blueprint(request)

    # Should still succeed and fill in defaults
    assert blueprint.title == "Incomplete Song"
    assert len(blueprint.sections) == 1
    assert blueprint.sections[0].id == "sec_verse1"
    assert blueprint.sections[0].bars > 0  # Should have default
    assert "sec_verse1" in blueprint.lyrics  # Should have filled in lyrics
    assert blueprint.vocal_style is not None


def test_llm_engine_fallback_on_error():
    """Test that LLM engine falls back to fake engine on errors."""
    # Create a fake LLM client that will raise an exception
    class ErrorLLMClient(FakeLLMClient):
        def generate_json(self, *args, **kwargs):
            raise Exception("API Error")

    error_llm = ErrorLLMClient()
    fallback = FakeSongBlueprintEngine()
    engine = LLMSongBlueprintEngine(llm_client=error_llm, fallback_engine=fallback)

    request = SongBlueprintRequest(
        prompt="A test song that will trigger fallback",
        genre="Rock",
        mood="Dark",
    )

    # Should not raise exception, should use fallback
    blueprint = engine.generate_blueprint(request)

    # Verify we got a response (from fallback engine)
    assert blueprint is not None
    assert blueprint.genre == "Rock"
    assert blueprint.mood == "Dark"
    assert len(blueprint.sections) > 0


def test_llm_engine_with_invalid_json():
    """Test LLM engine handles invalid JSON gracefully."""
    # Create a fake LLM that returns empty dict
    fake_llm = FakeLLMClient(mock_response={})
    fallback = FakeSongBlueprintEngine()
    engine = LLMSongBlueprintEngine(llm_client=fake_llm, fallback_engine=fallback)

    request = SongBlueprintRequest(
        prompt="A test song with invalid response",
        genre="Jazz",
        mood="Emotional",
    )

    # Should fall back due to missing sections
    blueprint = engine.generate_blueprint(request)

    assert blueprint is not None
    assert blueprint.genre == "Jazz"
    assert blueprint.mood == "Emotional"


def test_llm_engine_preserves_request_values():
    """Test that LLM engine uses request values when provided."""
    mock_response = {
        "title": "Test Song",
        "sections": [
            {"id": "sec_v1", "type": "verse", "name": "V1", "bars": 8}
        ],
        "lyrics": {"sec_v1": "Test lyrics"},
        "vocal_style": {"gender": "male", "tone": "smooth", "energy": "low"},
    }

    fake_llm = FakeLLMClient(mock_response=mock_response)
    engine = LLMSongBlueprintEngine(llm_client=fake_llm)

    # Provide specific BPM and key
    request = SongBlueprintRequest(
        prompt="Test song with specific parameters",
        genre="Lo-fi",
        mood="Chill",
        bpm=85,
        key="Dm",
    )

    blueprint = engine.generate_blueprint(request)

    # Should use the requested BPM and key
    assert blueprint.bpm == 85
    assert blueprint.key == "Dm"


def test_fake_llm_client():
    """Test the FakeLLMClient utility."""
    mock_data = {"test": "data"}
    client = FakeLLMClient(mock_response=mock_data)

    result = client.generate_json(prompt="test prompt")

    assert result == mock_data
