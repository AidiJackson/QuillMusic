"""
Instrumental render service - orchestrates rendering jobs
"""
import uuid
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.instrumental import InstrumentalRenderRequest, InstrumentalRenderStatus
from app.schemas.song import SongBlueprintResponse
from app.schemas.manual import ManualProject
from app.models.instrumental import InstrumentalJobModel
from app.models.blueprint import SongBlueprintModel
from app.models.manual import ManualProjectModel
from app.services.instrumental_engine import get_instrumental_engine

logger = logging.getLogger(__name__)


def create_instrumental_job(
    request: InstrumentalRenderRequest,
    db: Session
) -> InstrumentalRenderStatus:
    """
    Create and process an instrumental render job.

    This is currently synchronous for simplicity, but designed to be
    easily converted to async/background processing in the future.

    Args:
        request: The render request
        db: Database session

    Returns:
        InstrumentalRenderStatus with the job details

    Raises:
        ValueError: If source not found or invalid
    """
    # Create job ID
    job_id = str(uuid.uuid4())

    logger.info(f"Creating instrumental job {job_id} for {request.source_type}:{request.source_id}")

    try:
        # Create job record with "processing" status
        job = InstrumentalJobModel(
            id=job_id,
            status="processing",
            engine_type=request.engine_type,
            source_type=request.source_type,
            source_id=request.source_id,
        )
        db.add(job)
        db.commit()

        # Load source data and render
        audio_url, duration_seconds = _render_instrumental(request, db)

        # Update job to "ready"
        job.status = "ready"
        job.audio_url = audio_url
        job.duration_seconds = duration_seconds
        job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(job)

        logger.info(f"Instrumental job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Instrumental job {job_id} failed: {str(e)}")

        # Update job to "failed"
        job = db.query(InstrumentalJobModel).filter(InstrumentalJobModel.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(job)

        raise

    # Convert to response schema
    return _job_model_to_status(job)


def get_instrumental_job(job_id: str, db: Session) -> InstrumentalRenderStatus:
    """
    Get instrumental job status by ID.

    Args:
        job_id: The job ID
        db: Database session

    Returns:
        InstrumentalRenderStatus

    Raises:
        ValueError: If job not found
    """
    job = db.query(InstrumentalJobModel).filter(InstrumentalJobModel.id == job_id).first()

    if not job:
        raise ValueError(f"Instrumental job {job_id} not found")

    return _job_model_to_status(job)


def _render_instrumental(request: InstrumentalRenderRequest, db: Session) -> tuple[str, int]:
    """
    Internal function to perform the actual rendering.

    Args:
        request: The render request
        db: Database session

    Returns:
        Tuple of (audio_url, duration_seconds)
    """
    engine = get_instrumental_engine(request.engine_type)

    if request.source_type == "blueprint":
        # Load blueprint from database
        blueprint_model = db.query(SongBlueprintModel).filter(
            SongBlueprintModel.id == request.source_id
        ).first()

        if not blueprint_model:
            raise ValueError(f"Blueprint {request.source_id} not found")

        # Deserialize blueprint JSON
        blueprint_data = json.loads(blueprint_model.blueprint_json)
        blueprint = SongBlueprintResponse(**blueprint_data)

        # Render from blueprint
        audio_url, duration = engine.render_from_blueprint(blueprint)

    elif request.source_type == "manual_project":
        # Load manual project
        project_model = db.query(ManualProjectModel).filter(
            ManualProjectModel.id == request.source_id
        ).first()

        if not project_model:
            raise ValueError(f"Manual project {request.source_id} not found")

        # Convert to schema
        project = ManualProject(
            id=project_model.id,
            name=project_model.name,
            tempo_bpm=project_model.tempo_bpm,
            time_signature=project_model.time_signature,
            key=project_model.key,
            description=project_model.description,
            created_at=project_model.created_at,
            updated_at=project_model.updated_at,
        )

        # Get tracks and patterns
        tracks = project_model.tracks
        patterns = []
        for track in tracks:
            patterns.extend(track.patterns)

        # Render from manual project
        audio_url, duration = engine.render_from_manual_project(project, tracks, patterns)

    else:
        raise ValueError(f"Unknown source type: {request.source_type}")

    # If duration was specified in request, use that instead
    if request.duration_seconds:
        duration = request.duration_seconds

    return audio_url, duration


def _job_model_to_status(job: InstrumentalJobModel) -> InstrumentalRenderStatus:
    """Convert InstrumentalJobModel to InstrumentalRenderStatus."""
    return InstrumentalRenderStatus(
        id=job.id,
        status=job.status,
        engine_type=job.engine_type,
        source_type=job.source_type,
        source_id=job.source_id,
        duration_seconds=job.duration_seconds,
        audio_url=job.audio_url,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
