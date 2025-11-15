"""
Manual Creator schemas - DAW-style manual song projects
"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


# Instrument types for tracks
InstrumentType = Literal["drums", "bass", "chords", "lead", "fx", "vocal"]


# ========== Project Schemas ==========

class ManualProjectCreate(BaseModel):
    """Request schema for creating a manual project."""

    name: str = Field(..., description="Project name", min_length=1, max_length=200)
    tempo_bpm: int = Field(..., description="Tempo in beats per minute", ge=40, le=240)
    time_signature: str = Field(default="4/4", description="Time signature (e.g., '4/4', '3/4')")
    key: Optional[str] = Field(None, description="Musical key (e.g., 'C', 'Am')")
    description: Optional[str] = Field(None, description="Project description")


class ManualProject(BaseModel):
    """Response schema for a manual project."""

    id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    tempo_bpm: int = Field(..., description="Tempo in beats per minute")
    time_signature: str = Field(..., description="Time signature")
    key: Optional[str] = Field(None, description="Musical key")
    description: Optional[str] = Field(None, description="Project description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# ========== Track Schemas ==========

class TrackCreate(BaseModel):
    """Request schema for creating a track."""

    name: str = Field(..., description="Track name", min_length=1, max_length=100)
    instrument_type: InstrumentType = Field(..., description="Type of instrument")
    channel_index: int = Field(..., description="Channel index (0-based)", ge=0)


class TrackUpdate(BaseModel):
    """Request schema for updating a track."""

    name: Optional[str] = Field(None, description="Track name", min_length=1, max_length=100)
    volume: Optional[float] = Field(None, description="Volume (0.0-1.0)", ge=0.0, le=1.0)
    pan: Optional[float] = Field(None, description="Pan (-1.0 to 1.0)", ge=-1.0, le=1.0)
    muted: Optional[bool] = Field(None, description="Mute state")
    solo: Optional[bool] = Field(None, description="Solo state")
    channel_index: Optional[int] = Field(None, description="Channel index", ge=0)


class Track(BaseModel):
    """Response schema for a track."""

    id: str = Field(..., description="Unique track identifier")
    project_id: str = Field(..., description="Parent project ID")
    name: str = Field(..., description="Track name")
    instrument_type: InstrumentType = Field(..., description="Type of instrument")
    channel_index: int = Field(..., description="Channel index (0-based)")
    volume: float = Field(default=0.8, description="Volume (0.0-1.0)")
    pan: float = Field(default=0.0, description="Pan (-1.0 to 1.0)")
    muted: bool = Field(default=False, description="Mute state")
    solo: bool = Field(default=False, description="Solo state")


# ========== Pattern Schemas ==========

class PatternCreate(BaseModel):
    """Request schema for creating a pattern."""

    name: str = Field(..., description="Pattern name", min_length=1, max_length=100)
    length_bars: int = Field(..., description="Length in bars", ge=1, le=64)
    start_bar: int = Field(..., description="Start bar position on timeline", ge=0)


class PatternUpdate(BaseModel):
    """Request schema for updating a pattern."""

    name: Optional[str] = Field(None, description="Pattern name", min_length=1, max_length=100)
    length_bars: Optional[int] = Field(None, description="Length in bars", ge=1, le=64)
    start_bar: Optional[int] = Field(None, description="Start bar position", ge=0)


class Pattern(BaseModel):
    """Response schema for a pattern."""

    id: str = Field(..., description="Unique pattern identifier")
    track_id: str = Field(..., description="Parent track ID")
    name: str = Field(..., description="Pattern name")
    length_bars: int = Field(..., description="Length in bars")
    start_bar: int = Field(..., description="Start bar position on timeline")


# ========== Note Schemas ==========

class NoteCreate(BaseModel):
    """Request schema for creating a note."""

    pattern_id: str = Field(..., description="Parent pattern ID")
    step_index: int = Field(..., description="Grid step index (0-based)", ge=0)
    pitch: int = Field(..., description="MIDI pitch (0-127)", ge=0, le=127)
    velocity: int = Field(..., description="Velocity (0-127)", ge=0, le=127)


class Note(BaseModel):
    """Response schema for a note."""

    id: str = Field(..., description="Unique note identifier")
    pattern_id: str = Field(..., description="Parent pattern ID")
    step_index: int = Field(..., description="Grid step index (0-based)")
    pitch: int = Field(..., description="MIDI pitch (0-127)")
    velocity: int = Field(..., description="Velocity (0-127)")


# ========== Composite Response Schemas ==========

class ManualProjectDetail(BaseModel):
    """Detailed project response with all related data."""

    project: ManualProject = Field(..., description="Project information")
    tracks: list[Track] = Field(default_factory=list, description="All tracks in the project")
    patterns: list[Pattern] = Field(default_factory=list, description="All patterns across all tracks")
    notes: list[Note] = Field(default_factory=list, description="All notes across all patterns")
