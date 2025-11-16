"""
SQLAlchemy models for Instrumental rendering jobs
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime

from app.core.database import Base


class InstrumentalJobModel(Base):
    """Instrumental render job database model."""

    __tablename__ = "instrumental_jobs"

    id = Column(String, primary_key=True, index=True)
    status = Column(String(20), nullable=False, default="queued")  # queued, processing, ready, failed
    engine_type = Column(String(50), nullable=False, default="fake")
    model = Column(String(100), nullable=True)  # AI model name (e.g., "Stable Audio 2.0")
    source_type = Column(String(20), nullable=False)  # blueprint, manual_project
    source_id = Column(String, nullable=False, index=True)
    duration_seconds = Column(Integer, nullable=True)
    audio_url = Column(String(500), nullable=True)
    error_message = Column(String(1000), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
