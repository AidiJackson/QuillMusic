"""
Song blueprint schemas
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


# Section types for song structure
SectionType = Literal[
    "intro",
    "verse",
    "pre_chorus",
    "chorus",
    "bridge",
    "drop",
    "outro",
    "mix_segment",
]


class SectionSchema(BaseModel):
    """Schema for a song section."""

    id: str = Field(..., description="Unique identifier for the section")
    type: SectionType = Field(..., description="Type of section")
    name: str = Field(..., description="Display name for the section")
    bars: int = Field(..., description="Number of bars/measures in this section")
    mood: str = Field(..., description="Mood/vibe of this section")
    description: str = Field(..., description="Detailed description of the section")
    instruments: list[str] = Field(
        default_factory=list, description="Instruments to feature in this section"
    )


class VocalStyleSchema(BaseModel):
    """Schema for vocal style configuration."""

    gender: Literal["male", "female", "mixed", "auto"] = Field(
        ..., description="Vocal gender"
    )
    tone: str = Field(..., description="Vocal tone description (e.g., 'smooth', 'raspy')")
    energy: Literal["low", "medium", "high"] = Field(..., description="Vocal energy level")
    accent: Optional[str] = Field(None, description="Accent/dialect if any")


class SongBlueprintRequest(BaseModel):
    """Request schema for generating a song blueprint."""

    prompt: str = Field(
        ...,
        description="High-level description of the desired song",
        min_length=10,
    )
    genre: str = Field(..., description="Music genre")
    mood: str = Field(..., description="Overall mood/vibe")
    bpm: Optional[int] = Field(None, ge=40, le=200, description="Beats per minute")
    key: Optional[str] = Field(None, description="Musical key (e.g., 'C', 'Am')")
    duration_seconds: Optional[int] = Field(
        None, ge=15, le=600, description="Target duration in seconds"
    )
    reference_text: Optional[str] = Field(
        None, description="Additional reference or inspiration"
    )


class SongBlueprintResponse(BaseModel):
    """Response schema for a generated song blueprint."""

    song_id: str = Field(..., description="Unique song identifier")
    title: str = Field(..., description="Generated song title")
    genre: str = Field(..., description="Music genre")
    mood: str = Field(..., description="Overall mood/vibe")
    bpm: int = Field(..., description="Beats per minute")
    key: str = Field(..., description="Musical key")
    sections: list[SectionSchema] = Field(
        ..., description="List of song sections in order"
    )
    lyrics: dict[str, str] = Field(
        ..., description="Lyrics mapped by section_id"
    )
    vocal_style: VocalStyleSchema = Field(..., description="Vocal style configuration")
    notes: Optional[str] = Field(None, description="Additional production notes")
