"""
Instrumental rendering schemas
"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


# Engine and source types
InstrumentalEngineType = Literal["fake", "external_http"]
InstrumentalSourceType = Literal["blueprint", "manual_project"]


class InstrumentalRenderRequest(BaseModel):
    """Request schema for rendering an instrumental."""

    source_type: InstrumentalSourceType = Field(..., description="Type of source (blueprint or manual_project)")
    source_id: str = Field(..., description="ID of the blueprint or manual project")
    engine_type: InstrumentalEngineType = Field(default="fake", description="Engine to use for rendering")
    duration_seconds: Optional[int] = Field(None, ge=1, le=600, description="Duration in seconds (optional)")
    style_hint: Optional[str] = Field(None, description="Style hint for the engine (e.g., 'dark ambient trap')")
    quality: Optional[Literal["draft", "standard", "high"]] = Field(None, description="Render quality")


class InstrumentalRenderStatus(BaseModel):
    """Response schema for instrumental render job status."""

    id: str = Field(..., description="Job ID")
    status: Literal["queued", "processing", "ready", "failed"] = Field(..., description="Job status")
    engine_type: InstrumentalEngineType = Field(..., description="Engine used")
    source_type: InstrumentalSourceType = Field(..., description="Source type")
    source_id: str = Field(..., description="Source ID")
    duration_seconds: Optional[int] = Field(None, description="Duration in seconds")
    audio_url: Optional[str] = Field(None, description="URL to the rendered audio")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
