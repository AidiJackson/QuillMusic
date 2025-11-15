"""
Render job schemas
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


RenderType = Literal["instrumental", "vocals", "full_mix"]
RenderStatus = Literal["queued", "processing", "failed", "ready"]


class RenderJobCreate(BaseModel):
    """Request schema for creating a render job."""

    song_id: str = Field(..., description="ID of the song blueprint to render")
    render_type: RenderType = Field(
        ..., description="Type of render to produce"
    )


class RenderJobStatus(BaseModel):
    """Response schema for render job status."""

    job_id: str = Field(..., description="Unique job identifier")
    song_id: str = Field(..., description="ID of the song being rendered")
    render_type: RenderType = Field(..., description="Type of render")
    status: RenderStatus = Field(..., description="Current job status")
    audio_url: Optional[str] = Field(None, description="URL to the rendered audio file")
    error: Optional[str] = Field(None, description="Error message if failed")
