"""
SQLAlchemy models for Manual Creator (DAW Lite)
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class ManualProjectModel(Base):
    """Manual project database model."""

    __tablename__ = "manual_projects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    tempo_bpm = Column(Integer, nullable=False)
    time_signature = Column(String(10), nullable=False, default="4/4")
    key = Column(String(10), nullable=True)
    description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tracks = relationship("TrackModel", back_populates="project", cascade="all, delete-orphan")


class TrackModel(Base):
    """Track database model."""

    __tablename__ = "tracks"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("manual_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    instrument_type = Column(String(20), nullable=False)  # drums, bass, chords, lead, fx, vocal
    channel_index = Column(Integer, nullable=False)
    volume = Column(Float, nullable=False, default=0.8)
    pan = Column(Float, nullable=False, default=0.0)
    muted = Column(Boolean, nullable=False, default=False)
    solo = Column(Boolean, nullable=False, default=False)

    # Relationships
    project = relationship("ManualProjectModel", back_populates="tracks")
    patterns = relationship("PatternModel", back_populates="track", cascade="all, delete-orphan")


class PatternModel(Base):
    """Pattern database model."""

    __tablename__ = "patterns"

    id = Column(String, primary_key=True, index=True)
    track_id = Column(String, ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    length_bars = Column(Integer, nullable=False)
    start_bar = Column(Integer, nullable=False)

    # Relationships
    track = relationship("TrackModel", back_populates="patterns")
    notes = relationship("NoteModel", back_populates="pattern", cascade="all, delete-orphan")


class NoteModel(Base):
    """Note database model."""

    __tablename__ = "notes"

    id = Column(String, primary_key=True, index=True)
    pattern_id = Column(String, ForeignKey("patterns.id", ondelete="CASCADE"), nullable=False, index=True)
    step_index = Column(Integer, nullable=False)
    pitch = Column(Integer, nullable=False)
    velocity = Column(Integer, nullable=False)

    # Relationships
    pattern = relationship("PatternModel", back_populates="notes")
