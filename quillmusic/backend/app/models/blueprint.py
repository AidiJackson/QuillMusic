"""
SQLAlchemy models for storing song blueprints
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime

from app.core.database import Base


class SongBlueprintModel(Base):
    """Song blueprint storage model."""

    __tablename__ = "song_blueprints"

    id = Column(String, primary_key=True, index=True)  # song_id
    title = Column(String(200), nullable=False)
    genre = Column(String(100), nullable=False)
    mood = Column(String(100), nullable=False)
    bpm = Column(Integer, nullable=False)
    key = Column(String(10), nullable=False)
    blueprint_json = Column(Text, nullable=False)  # Full blueprint as JSON
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
