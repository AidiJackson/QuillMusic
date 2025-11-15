"""
Song Blueprint Generation Service

This module contains engines for generating song blueprints.
Currently implements a fake/mock engine for development and testing.
"""
import hashlib
import uuid
from abc import ABC, abstractmethod

from app.schemas.song import (
    SongBlueprintRequest,
    SongBlueprintResponse,
    SectionSchema,
    VocalStyleSchema,
    SectionType,
)


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


# Global singleton instance
_blueprint_engine: SongBlueprintEngine = FakeSongBlueprintEngine()


def get_blueprint_engine() -> SongBlueprintEngine:
    """Get the song blueprint engine (currently fake, can be swapped later)."""
    return _blueprint_engine
