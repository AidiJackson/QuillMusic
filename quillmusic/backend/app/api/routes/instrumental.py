"""
Instrumental rendering API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.instrumental import InstrumentalRenderRequest, InstrumentalRenderStatus
from app.services.instrumental_render_service import create_instrumental_job, get_instrumental_job

router = APIRouter(prefix="/instrumental", tags=["instrumental"])


@router.post("/render", response_model=InstrumentalRenderStatus)
def render_instrumental(
    request: InstrumentalRenderRequest,
    db: Session = Depends(get_db),
):
    """
    Render an instrumental from a blueprint or manual project.

    Currently synchronous - returns immediately with status="ready".
    Future phases will use background job queue for async processing.
    """
    try:
        status = create_instrumental_job(request, db)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Render failed: {str(e)}")


@router.get("/jobs/{job_id}", response_model=InstrumentalRenderStatus)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    """Get the status of an instrumental render job."""
    try:
        status = get_instrumental_job(job_id, db)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")
