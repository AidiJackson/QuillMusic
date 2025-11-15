"""
Song Blueprint Generation Service

This module contains engines for generating song blueprints.
Supports both fake/mock engines for development and LLM-powered engines.
"""
import hashlib
import uuid
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

from app.schemas.song import (
    SongBlueprintRequest,
    SongBlueprintResponse,
    SectionSchema,
    VocalStyleSchema,
    SectionType,
)
from app.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class SongBlueprintEngine(ABC):
    """Abstract base class for song blueprint generation engines."""

    @abstractmethod
    def generate_blueprint(
        self, req: SongBlueprintRequest
    ) -> SongBlueprintResponse:
        """Generate a song blueprint from a request."""
        pass


class FakeSongBlueprintEngine(SongBlueprintEngine):
    """
    Fake song blueprint engine for development and testing.

    Generates deterministic, reasonable song blueprints without
    calling any external APIs or ML models.
    """

    def generate_blueprint(
        self, req: SongBlueprintRequest
    ) -> SongBlueprintResponse:
        """Generate a fake but reasonable song blueprint."""
        # Create deterministic song_id based on prompt
        song_id = self._generate_song_id(req.prompt)

        # Generate title
        title = self._generate_title(req.genre, req.mood, req.prompt)

        # Set defaults
        bpm = req.bpm or self._default_bpm_for_genre(req.genre)
        key = req.key or self._default_key_for_mood(req.mood)
        duration = req.duration_seconds or 180  # Default 3 minutes

        # Generate sections
        sections = self._generate_sections(req.genre, req.mood, duration, bpm)

        # Generate lyrics for each section
        lyrics = self._generate_lyrics(sections, req.prompt, req.mood)

        # Generate vocal style
        vocal_style = self._generate_vocal_style(req.genre, req.mood)

        # Generate production notes
        notes = self._generate_notes(req.genre, req.mood, sections)

        return SongBlueprintResponse(
            song_id=song_id,
            title=title,
            genre=req.genre,
            mood=req.mood,
            bpm=bpm,
            key=key,
            sections=sections,
            lyrics=lyrics,
            vocal_style=vocal_style,
            notes=notes,
        )

    def _generate_song_id(self, prompt: str) -> str:
        """Generate a deterministic song ID from the prompt."""
        # Use first 12 chars of hash for determinism, but add UUID for uniqueness
        hash_prefix = hashlib.md5(prompt.encode()).hexdigest()[:8]
        return f"song_{hash_prefix}_{uuid.uuid4().hex[:8]}"

    def _generate_title(self, genre: str, mood: str, prompt: str) -> str:
        """Generate a song title."""
        # Simple title generation based on mood and genre
        mood_words = {
            "Dark": ["Shadows", "Midnight", "Eclipse", "Void"],
            "Emotional": ["Hearts", "Memories", "Dreams", "Echoes"],
            "Energetic": ["Thunder", "Lightning", "Fire", "Rush"],
            "Chill": ["Waves", "Sunset", "Breeze", "Float"],
            "Uplifting": ["Rising", "Soar", "Shine", "Hope"],
        }

        genre_words = {
            "Pop": ["Love", "Tonight", "Forever", "Dance"],
            "Hip Hop": ["Streets", "Real", "Money", "Hustle"],
            "EDM": ["Drop", "Bass", "Rave", "Electric"],
            "Lo-fi": ["Study", "Cafe", "Rain", "Vibes"],
            "Trap": ["Trap", "Wavy", "Flex", "Drip"],
            "Ambient": ["Space", "Drift", "Cosmos", "Flow"],
            "Rock": ["Rebel", "Wild", "Storm", "Edge"],
        }

        # Get word based on hash of prompt
        hash_val = int(hashlib.md5(prompt.encode()).hexdigest(), 16)
        mood_word = mood_words.get(mood, ["Untitled"])[hash_val % len(mood_words.get(mood, ["Untitled"]))]
        genre_word = genre_words.get(genre, ["Song"])[hash_val % len(genre_words.get(genre, ["Song"]))]

        return f"{mood_word} {genre_word}"

    def _default_bpm_for_genre(self, genre: str) -> int:
        """Get default BPM for a genre."""
        bpm_map = {
            "Pop": 120,
            "Hip Hop": 90,
            "EDM": 128,
            "Lo-fi": 80,
            "Trap": 140,
            "Ambient": 70,
            "Rock": 130,
        }
        return bpm_map.get(genre, 120)

    def _default_key_for_mood(self, mood: str) -> str:
        """Get default key for a mood."""
        key_map = {
            "Dark": "Am",
            "Emotional": "Dm",
            "Energetic": "C",
            "Chill": "G",
            "Uplifting": "D",
        }
        return key_map.get(mood, "C")

    def _generate_sections(
        self, genre: str, mood: str, duration: int, bpm: int
    ) -> list[SectionSchema]:
        """Generate song sections."""
        # Calculate approximate bars based on duration and BPM
        # Assuming 4/4 time signature
        seconds_per_bar = (60 / bpm) * 4
        total_bars = int(duration / seconds_per_bar)

        sections = []

        # Intro
        sections.append(
            SectionSchema(
                id="sec_intro",
                type="intro",
                name="Intro",
                bars=8,
                mood=mood,
                description=f"Opening {genre} intro setting the {mood.lower()} atmosphere",
                instruments=self._get_instruments_for_genre(genre, "intro"),
            )
        )

        # Verse 1
        sections.append(
            SectionSchema(
                id="sec_verse1",
                type="verse",
                name="Verse 1",
                bars=16,
                mood=mood,
                description="First verse introducing the story",
                instruments=self._get_instruments_for_genre(genre, "verse"),
            )
        )

        # Pre-Chorus (if longer song)
        if total_bars > 64:
            sections.append(
                SectionSchema(
                    id="sec_prechorus1",
                    type="pre_chorus",
                    name="Pre-Chorus 1",
                    bars=8,
                    mood=mood,
                    description="Building tension before the chorus",
                    instruments=self._get_instruments_for_genre(genre, "pre_chorus"),
                )
            )

        # Chorus
        sections.append(
            SectionSchema(
                id="sec_chorus1",
                type="chorus",
                name="Chorus",
                bars=16,
                mood=mood,
                description="Main hook and chorus",
                instruments=self._get_instruments_for_genre(genre, "chorus"),
            )
        )

        # Verse 2
        sections.append(
            SectionSchema(
                id="sec_verse2",
                type="verse",
                name="Verse 2",
                bars=16,
                mood=mood,
                description="Second verse developing the narrative",
                instruments=self._get_instruments_for_genre(genre, "verse"),
            )
        )

        # Chorus 2
        sections.append(
            SectionSchema(
                id="sec_chorus2",
                type="chorus",
                name="Chorus 2",
                bars=16,
                mood=mood,
                description="Chorus repetition with variations",
                instruments=self._get_instruments_for_genre(genre, "chorus"),
            )
        )

        # Bridge
        sections.append(
            SectionSchema(
                id="sec_bridge",
                type="bridge",
                name="Bridge",
                bars=8,
                mood=mood,
                description="Bridge providing contrast and emotional peak",
                instruments=self._get_instruments_for_genre(genre, "bridge"),
            )
        )

        # Final Chorus
        sections.append(
            SectionSchema(
                id="sec_chorus_final",
                type="chorus",
                name="Final Chorus",
                bars=16,
                mood=mood,
                description="Final chorus with full energy",
                instruments=self._get_instruments_for_genre(genre, "chorus"),
            )
        )

        # Outro
        sections.append(
            SectionSchema(
                id="sec_outro",
                type="outro",
                name="Outro",
                bars=8,
                mood=mood,
                description="Closing section bringing resolution",
                instruments=self._get_instruments_for_genre(genre, "outro"),
            )
        )

        return sections

    def _get_instruments_for_genre(
        self, genre: str, section: str
    ) -> list[str]:
        """Get instrument list for genre and section."""
        genre_instruments = {
            "Pop": ["synth", "drums", "bass", "guitar", "piano"],
            "Hip Hop": ["drums", "808bass", "synth", "sample"],
            "EDM": ["synth", "drums", "bass", "pad", "lead"],
            "Lo-fi": ["piano", "drums", "bass", "vinyl", "ambient"],
            "Trap": ["hi-hats", "808", "synth", "snare"],
            "Ambient": ["pad", "synth", "reverb", "atmosphere"],
            "Rock": ["guitar", "drums", "bass", "vocals"],
        }

        base_instruments = genre_instruments.get(
            genre, ["synth", "drums", "bass"]
        )

        # Vary instruments by section
        if section == "intro":
            return base_instruments[:2]  # Sparse intro
        elif section == "chorus":
            return base_instruments  # Full instrumentation
        else:
            return base_instruments[:3]  # Medium instrumentation

    def _generate_lyrics(
        self, sections: list[SectionSchema], prompt: str, mood: str
    ) -> dict[str, str]:
        """Generate simple placeholder lyrics for each section."""
        lyrics = {}

        for section in sections:
            if section.type == "intro" or section.type == "outro":
                lyrics[section.id] = "[Instrumental]"
            elif section.type == "verse":
                lyrics[section.id] = f"""In the {mood.lower()} of the night
Walking through these feelings inside
Every moment tells a story
{prompt[:50]}..."""
            elif section.type == "chorus":
                lyrics[section.id] = f"""This is where we come alive
Feel the rhythm, feel the vibe
{mood} hearts beating as one
This is how it's begun"""
            elif section.type == "pre_chorus":
                lyrics[section.id] = """Building up, rising high
Can you feel it in the sky"""
            elif section.type == "bridge":
                lyrics[section.id] = f"""Break it down, change the flow
Let the {mood.lower()} emotions show
Take a breath, feel the change
Rearrange, rearrange"""
            else:
                lyrics[section.id] = "[To be written]"

        return lyrics

    def _generate_vocal_style(
        self, genre: str, mood: str
    ) -> VocalStyleSchema:
        """Generate vocal style based on genre and mood."""
        # Map genre to typical vocal characteristics
        genre_vocal_map = {
            "Pop": {"gender": "female", "tone": "smooth", "energy": "medium"},
            "Hip Hop": {"gender": "male", "tone": "confident", "energy": "medium"},
            "EDM": {"gender": "female", "tone": "bright", "energy": "high"},
            "Lo-fi": {"gender": "mixed", "tone": "soft", "energy": "low"},
            "Trap": {"gender": "male", "tone": "autotuned", "energy": "high"},
            "Ambient": {"gender": "female", "tone": "ethereal", "energy": "low"},
            "Rock": {"gender": "male", "tone": "raspy", "energy": "high"},
        }

        defaults = genre_vocal_map.get(
            genre, {"gender": "auto", "tone": "neutral", "energy": "medium"}
        )

        return VocalStyleSchema(
            gender=defaults["gender"],
            tone=defaults["tone"],
            energy=defaults["energy"],
            accent=None,
        )

    def _generate_notes(
        self, genre: str, mood: str, sections: list[SectionSchema]
    ) -> str:
        """Generate production notes."""
        return f"""Production Notes:
- Genre: {genre} with {mood.lower()} atmosphere
- Total sections: {len(sections)}
- Keep dynamics varying between sections
- Add automation and fills for transitions
- Consider layering vocals in chorus
- Master with {genre}-appropriate compression and EQ"""


class LLMSongBlueprintEngine(SongBlueprintEngine):
    """
    LLM-powered song blueprint engine.

    Uses a Large Language Model to generate creative, coherent song structures
    and lyrics based on user input. Falls back to FakeSongBlueprintEngine if
    LLM calls fail.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        fallback_engine: Optional[SongBlueprintEngine] = None,
    ):
        """
        Initialize the LLM song blueprint engine.

        Args:
            llm_client: The LLM client to use for generation
            fallback_engine: Optional fallback engine if LLM fails (defaults to FakeSongBlueprintEngine)
        """
        self.llm_client = llm_client
        self.fallback_engine = fallback_engine or FakeSongBlueprintEngine()

    def generate_blueprint(
        self, req: SongBlueprintRequest
    ) -> SongBlueprintResponse:
        """Generate a song blueprint using an LLM."""
        try:
            logger.info(
                f"Generating LLM-powered blueprint: genre={req.genre}, mood={req.mood}"
            )

            # Construct the prompt for the LLM
            prompt = self._build_llm_prompt(req)
            system_prompt = self._build_system_prompt()

            # Call LLM
            response_json = self.llm_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.8,
                max_tokens=3000,
            )

            # Parse and validate the response
            blueprint = self._parse_llm_response(response_json, req)

            logger.info(
                f"Successfully generated LLM blueprint: song_id={blueprint.song_id}"
            )

            return blueprint

        except Exception as e:
            logger.warning(
                f"LLM blueprint generation failed, falling back to fake engine: {e}"
            )
            # Fall back to the fake engine
            return self.fallback_engine.generate_blueprint(req)

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the LLM."""
        return """You are an expert music producer and songwriter. Your task is to generate detailed song blueprints including structure, lyrics, and production notes.

You must respond with ONLY valid JSON matching this exact schema:

{
  "title": "string (creative song title)",
  "sections": [
    {
      "id": "string (e.g., 'sec_intro', 'sec_verse1')",
      "type": "string (one of: intro, verse, pre_chorus, chorus, bridge, drop, outro, mix_segment)",
      "name": "string (e.g., 'Verse 1', 'Chorus')",
      "bars": number (typically 4, 8, or 16),
      "mood": "string",
      "description": "string (detailed description of this section)",
      "instruments": ["array", "of", "strings"]
    }
  ],
  "lyrics": {
    "sec_id": "lyrics for that section as a multi-line string"
  },
  "vocal_style": {
    "gender": "string (male/female/mixed/auto)",
    "tone": "string (e.g., 'smooth', 'raspy', 'powerful')",
    "energy": "string (low/medium/high)",
    "accent": "string or null"
  },
  "notes": "string (production notes and recommendations)"
}

Make the song structure logical and musically sound. Lyrics should be creative, coherent, and match the mood/genre. Include realistic instrument choices for each section."""

    def _build_llm_prompt(self, req: SongBlueprintRequest) -> str:
        """Build the user prompt for the LLM."""
        prompt_parts = [
            f"Generate a complete song blueprint with the following specifications:",
            f"",
            f"Genre: {req.genre}",
            f"Mood: {req.mood}",
            f"User Description: {req.prompt}",
        ]

        if req.bpm:
            prompt_parts.append(f"Target BPM: {req.bpm}")
        if req.key:
            prompt_parts.append(f"Musical Key: {req.key}")
        if req.duration_seconds:
            prompt_parts.append(
                f"Target Duration: approximately {req.duration_seconds} seconds"
            )
        if req.reference_text:
            prompt_parts.append(f"Additional Reference: {req.reference_text}")

        prompt_parts.extend(
            [
                "",
                "Requirements:",
                "- Create a complete song structure with intro, verses, chorus, bridge, and outro",
                "- Generate creative, meaningful lyrics for each section (except instrumental parts)",
                "- Choose appropriate instruments for the genre",
                "- Ensure the song has good flow and dynamics",
                "- Respond with ONLY the JSON, no additional text",
            ]
        )

        return "\n".join(prompt_parts)

    def _parse_llm_response(
        self, response_json: dict, req: SongBlueprintRequest
    ) -> SongBlueprintResponse:
        """
        Parse and validate the LLM's JSON response.

        Args:
            response_json: The JSON response from the LLM
            req: The original request (for fallback values)

        Returns:
            A validated SongBlueprintResponse

        Raises:
            ValueError: If response is invalid and cannot be fixed
        """
        # Generate song_id
        song_id = f"song_{hashlib.md5(req.prompt.encode()).hexdigest()[:8]}_{uuid.uuid4().hex[:8]}"

        # Extract and validate title
        title = response_json.get("title", "Untitled Song")

        # Parse sections
        sections_data = response_json.get("sections", [])
        if not sections_data:
            raise ValueError("No sections in LLM response")

        sections = []
        for sec in sections_data:
            sections.append(
                SectionSchema(
                    id=sec.get("id", f"sec_{len(sections)}"),
                    type=sec.get("type", "verse"),
                    name=sec.get("name", f"Section {len(sections) + 1}"),
                    bars=sec.get("bars", 8),
                    mood=sec.get("mood", req.mood),
                    description=sec.get("description", ""),
                    instruments=sec.get("instruments", []),
                )
            )

        # Parse lyrics
        lyrics = response_json.get("lyrics", {})
        # Ensure all sections have lyrics
        for section in sections:
            if section.id not in lyrics:
                if section.type in ["intro", "outro", "drop"]:
                    lyrics[section.id] = "[Instrumental]"
                else:
                    lyrics[section.id] = "[To be written]"

        # Parse vocal style
        vocal_data = response_json.get("vocal_style", {})
        vocal_style = VocalStyleSchema(
            gender=vocal_data.get("gender", "auto"),
            tone=vocal_data.get("tone", "neutral"),
            energy=vocal_data.get("energy", "medium"),
            accent=vocal_data.get("accent"),
        )

        # Set defaults from request or use sensible defaults
        bpm = req.bpm or 120
        key = req.key or "C"

        return SongBlueprintResponse(
            song_id=song_id,
            title=title,
            genre=req.genre,
            mood=req.mood,
            bpm=bpm,
            key=key,
            sections=sections,
            lyrics=lyrics,
            vocal_style=vocal_style,
            notes=response_json.get("notes"),
        )


# Global singleton instance (default to fake for backward compatibility)
_blueprint_engine: SongBlueprintEngine = FakeSongBlueprintEngine()


def get_blueprint_engine() -> SongBlueprintEngine:
    """
    Get the song blueprint engine.

    This function returns the globally configured blueprint engine.
    Use get_configured_blueprint_engine() for dependency injection.
    """
    return _blueprint_engine
