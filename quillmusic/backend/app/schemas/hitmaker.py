"""
HitMaker Engine schemas for song analysis and AI-driven improvement suggestions.

This module provides Pydantic models for:
- Song DNA analysis (energy curves, tension, hooks)
- HitScore breakdown (overall quality metrics)
- Influence-based rewriting and suggestions
"""

from typing import Optional
from pydantic import BaseModel, Field


class SectionEnergy(BaseModel):
    """Energy and tension analysis for a specific song section."""

    name: str = Field(..., description="Section name (e.g., 'Intro', 'Verse 1', 'Chorus')")
    position_index: int = Field(..., ge=0, description="0-based index in the song")
    energy: float = Field(..., ge=0.0, le=1.0, description="Energy level (0.0-1.0)")
    tension: float = Field(..., ge=0.0, le=1.0, description="Tension level (0.0-1.0)")
    hook_density: float = Field(..., ge=0.0, le=1.0, description="Catchiness/hook density (0.0-1.0)")
    notes: Optional[str] = Field(None, description="Textual description of this section")


class SongDNA(BaseModel):
    """Complete DNA profile of a song's structure and emotional arc."""

    blueprint_id: Optional[str] = Field(None, description="Source blueprint ID if from AI Song Builder")
    manual_project_id: Optional[str] = Field(None, description="Source manual project ID if from Manual Creator")
    sections: list[SectionEnergy] = Field(..., description="Per-section energy/tension analysis")
    global_energy_curve: list[float] = Field(..., description="Normalized energy curve across song")
    global_tension_curve: list[float] = Field(..., description="Normalized tension curve across song")
    dominant_mood: str = Field(..., description="Overall mood (e.g., 'energetic', 'melancholic', 'uplifting')")
    genre_guess: str = Field(..., description="Predicted genre based on structure")
    structure_notes: list[str] = Field(..., description="Textual observations about song structure")


class HitScoreBreakdown(BaseModel):
    """Detailed breakdown of song's commercial potential."""

    overall: float = Field(..., ge=0.0, le=100.0, description="Overall hit potential (0-100)")
    hook_strength: float = Field(..., ge=0.0, le=100.0, description="Catchiness of hooks (0-100)")
    structure: float = Field(..., ge=0.0, le=100.0, description="Song structure quality (0-100)")
    lyrics_emotion: float = Field(..., ge=0.0, le=100.0, description="Emotional impact of lyrics (0-100)")
    genre_fit: float = Field(..., ge=0.0, le=100.0, description="How well it fits genre conventions (0-100)")
    originality: float = Field(..., ge=0.0, le=100.0, description="Uniqueness and innovation (0-100)")
    replay_value: float = Field(..., ge=0.0, le=100.0, description="Likelihood of repeated listens (0-100)")


class HitMakerAnalysis(BaseModel):
    """Complete analysis of a song with DNA, scores, and insights."""

    dna: SongDNA = Field(..., description="Song DNA profile")
    score: HitScoreBreakdown = Field(..., description="Hit potential scores")
    commentary: list[str] = Field(..., description="Bullet-point analysis notes")
    risks: list[str] = Field(..., description="What might hold the song back")
    opportunities: list[str] = Field(..., description="What to lean into more")


class InfluenceDescriptor(BaseModel):
    """Description of an artistic influence to apply."""

    name: str = Field(..., description="Artist or style name (e.g., 'The Weeknd', 'Billie Eilish')")
    weight: float = Field(..., ge=0.0, le=1.0, description="Influence strength (0.0-1.0)")


class HitMakerInfluenceRequest(BaseModel):
    """Request to apply artistic influences to a song."""

    source_blueprint_id: Optional[str] = Field(None, description="Source blueprint ID")
    source_manual_project_id: Optional[str] = Field(None, description="Source manual project ID")
    influences: list[InfluenceDescriptor] = Field(..., description="Artistic influences to apply")
    target_mood: Optional[str] = Field(None, description="Desired mood shift")
    target_genre: Optional[str] = Field(None, description="Desired genre shift")


class HitMakerInfluenceResponse(BaseModel):
    """Response with influence-adjusted DNA and creative suggestions."""

    adjusted_dna: SongDNA = Field(..., description="Modified song DNA with influences applied")
    hook_suggestions: list[str] = Field(..., description="Short hook concepts/lines")
    chorus_rewrite_ideas: list[str] = Field(..., description="Suggestions for chorus improvement")
    structure_suggestions: list[str] = Field(..., description="Structural changes (e.g., 'Move the drop earlier')")
    instrumentation_ideas: list[str] = Field(..., description="Instrumentation recommendations")
    vocal_style_notes: list[str] = Field(..., description="Vocal delivery suggestions")
