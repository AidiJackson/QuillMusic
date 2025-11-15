"""
Render Job API endpoints
"""
from fastapi import APIRouter, HTTPException

from app.schemas.render import RenderJobCreate, RenderJobStatus
from app.services.render_engine import get_render_engine

router = APIRouter()


@router.post("/renders", response_model=RenderJobStatus)
async def create_render_job(request: RenderJobCreate):
    """
    Create a new render job.

    Submits a song blueprint for rendering (instrumental, vocals, or full mix).
    Returns job status with job_id for tracking.
    """
    try:
        engine = get_render_engine()
        job_id = engine.submit(request.song_id, request.render_type)
        status = engine.status(job_id)
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create render job: {str(e)}",
        )


@router.get("/renders/{job_id}", response_model=RenderJobStatus)
async def get_render_status(job_id: str):
    """
    Get the status of a render job.

    Returns current status, and audio URL if ready.
    """
    try:
        engine = get_render_engine()
        status = engine.status(job_id)
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}",
        )
