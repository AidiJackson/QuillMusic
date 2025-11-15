"""
Manual Creator API routes - DAW-style manual song projects
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.manual import (
    ManualProjectModel,
    TrackModel,
    PatternModel,
    NoteModel,
)
from app.schemas.manual import (
    ManualProjectCreate,
    ManualProject,
    ManualProjectDetail,
    TrackCreate,
    TrackUpdate,
    Track,
    PatternCreate,
    PatternUpdate,
    Pattern,
    NoteCreate,
    Note,
)

router = APIRouter(prefix="/manual", tags=["manual"])


# ========== Helper Functions ==========

def model_to_project(model: ManualProjectModel) -> ManualProject:
    """Convert ManualProjectModel to ManualProject schema."""
    return ManualProject(
        id=model.id,
        name=model.name,
        tempo_bpm=model.tempo_bpm,
        time_signature=model.time_signature,
        key=model.key,
        description=model.description,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def model_to_track(model: TrackModel) -> Track:
    """Convert TrackModel to Track schema."""
    return Track(
        id=model.id,
        project_id=model.project_id,
        name=model.name,
        instrument_type=model.instrument_type,
        channel_index=model.channel_index,
        volume=model.volume,
        pan=model.pan,
        muted=model.muted,
        solo=model.solo,
    )


def model_to_pattern(model: PatternModel) -> Pattern:
    """Convert PatternModel to Pattern schema."""
    return Pattern(
        id=model.id,
        track_id=model.track_id,
        name=model.name,
        length_bars=model.length_bars,
        start_bar=model.start_bar,
    )


def model_to_note(model: NoteModel) -> Note:
    """Convert NoteModel to Note schema."""
    return Note(
        id=model.id,
        pattern_id=model.pattern_id,
        step_index=model.step_index,
        pitch=model.pitch,
        velocity=model.velocity,
    )


# ========== Project Endpoints ==========

@router.post("/projects", response_model=ManualProject)
def create_project(
    project: ManualProjectCreate,
    db: Session = Depends(get_db),
):
    """Create a new manual project."""
    db_project = ManualProjectModel(
        id=str(uuid.uuid4()),
        name=project.name,
        tempo_bpm=project.tempo_bpm,
        time_signature=project.time_signature,
        key=project.key,
        description=project.description,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return model_to_project(db_project)


@router.get("/projects", response_model=List[ManualProject])
def list_projects(db: Session = Depends(get_db)):
    """List all manual projects."""
    projects = db.query(ManualProjectModel).order_by(ManualProjectModel.updated_at.desc()).all()
    return [model_to_project(p) for p in projects]


@router.get("/projects/{project_id}", response_model=ManualProjectDetail)
def get_project_detail(
    project_id: str,
    db: Session = Depends(get_db),
):
    """Get detailed project information including all tracks, patterns, and notes."""
    # Fetch project
    project = db.query(ManualProjectModel).filter(ManualProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Fetch all tracks for this project
    tracks = db.query(TrackModel).filter(TrackModel.project_id == project_id).order_by(TrackModel.channel_index).all()
    track_ids = [t.id for t in tracks]

    # Fetch all patterns for these tracks
    patterns = []
    if track_ids:
        patterns = db.query(PatternModel).filter(PatternModel.track_id.in_(track_ids)).all()
    pattern_ids = [p.id for p in patterns]

    # Fetch all notes for these patterns
    notes = []
    if pattern_ids:
        notes = db.query(NoteModel).filter(NoteModel.pattern_id.in_(pattern_ids)).all()

    return ManualProjectDetail(
        project=model_to_project(project),
        tracks=[model_to_track(t) for t in tracks],
        patterns=[model_to_pattern(p) for p in patterns],
        notes=[model_to_note(n) for n in notes],
    )


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
):
    """Delete a project and all its related data."""
    project = db.query(ManualProjectModel).filter(ManualProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


# ========== Track Endpoints ==========

@router.post("/projects/{project_id}/tracks", response_model=Track)
def create_track(
    project_id: str,
    track: TrackCreate,
    db: Session = Depends(get_db),
):
    """Create a new track for a project."""
    # Verify project exists
    project = db.query(ManualProjectModel).filter(ManualProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_track = TrackModel(
        id=str(uuid.uuid4()),
        project_id=project_id,
        name=track.name,
        instrument_type=track.instrument_type,
        channel_index=track.channel_index,
    )
    db.add(db_track)
    db.commit()
    db.refresh(db_track)
    return model_to_track(db_track)


@router.patch("/tracks/{track_id}", response_model=Track)
def update_track(
    track_id: str,
    update: TrackUpdate,
    db: Session = Depends(get_db),
):
    """Update track properties."""
    track = db.query(TrackModel).filter(TrackModel.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Update fields if provided
    if update.name is not None:
        track.name = update.name
    if update.volume is not None:
        track.volume = update.volume
    if update.pan is not None:
        track.pan = update.pan
    if update.muted is not None:
        track.muted = update.muted
    if update.solo is not None:
        track.solo = update.solo
    if update.channel_index is not None:
        track.channel_index = update.channel_index

    db.commit()
    db.refresh(track)
    return model_to_track(track)


@router.delete("/tracks/{track_id}")
def delete_track(
    track_id: str,
    db: Session = Depends(get_db),
):
    """Delete a track and all its patterns/notes."""
    track = db.query(TrackModel).filter(TrackModel.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    db.delete(track)
    db.commit()
    return {"message": "Track deleted successfully"}


# ========== Pattern Endpoints ==========

@router.post("/tracks/{track_id}/patterns", response_model=Pattern)
def create_pattern(
    track_id: str,
    pattern: PatternCreate,
    db: Session = Depends(get_db),
):
    """Create a new pattern for a track."""
    # Verify track exists
    track = db.query(TrackModel).filter(TrackModel.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    db_pattern = PatternModel(
        id=str(uuid.uuid4()),
        track_id=track_id,
        name=pattern.name,
        length_bars=pattern.length_bars,
        start_bar=pattern.start_bar,
    )
    db.add(db_pattern)
    db.commit()
    db.refresh(db_pattern)
    return model_to_pattern(db_pattern)


@router.patch("/patterns/{pattern_id}", response_model=Pattern)
def update_pattern(
    pattern_id: str,
    update: PatternUpdate,
    db: Session = Depends(get_db),
):
    """Update pattern properties."""
    pattern = db.query(PatternModel).filter(PatternModel.id == pattern_id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    # Update fields if provided
    if update.name is not None:
        pattern.name = update.name
    if update.length_bars is not None:
        pattern.length_bars = update.length_bars
    if update.start_bar is not None:
        pattern.start_bar = update.start_bar

    db.commit()
    db.refresh(pattern)
    return model_to_pattern(pattern)


@router.delete("/patterns/{pattern_id}")
def delete_pattern(
    pattern_id: str,
    db: Session = Depends(get_db),
):
    """Delete a pattern and all its notes."""
    pattern = db.query(PatternModel).filter(PatternModel.id == pattern_id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    db.delete(pattern)
    db.commit()
    return {"message": "Pattern deleted successfully"}


# ========== Note Endpoints ==========

@router.get("/patterns/{pattern_id}/notes", response_model=List[Note])
def get_pattern_notes(
    pattern_id: str,
    db: Session = Depends(get_db),
):
    """Get all notes for a pattern."""
    # Verify pattern exists
    pattern = db.query(PatternModel).filter(PatternModel.id == pattern_id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    notes = db.query(NoteModel).filter(NoteModel.pattern_id == pattern_id).order_by(NoteModel.step_index).all()
    return [model_to_note(n) for n in notes]


@router.post("/patterns/{pattern_id}/notes/bulk", response_model=List[Note])
def replace_pattern_notes(
    pattern_id: str,
    notes: List[NoteCreate],
    db: Session = Depends(get_db),
):
    """Replace all notes for a pattern (bulk update)."""
    # Verify pattern exists
    pattern = db.query(PatternModel).filter(PatternModel.id == pattern_id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    # Delete all existing notes for this pattern
    db.query(NoteModel).filter(NoteModel.pattern_id == pattern_id).delete()

    # Create new notes
    db_notes = []
    for note in notes:
        db_note = NoteModel(
            id=str(uuid.uuid4()),
            pattern_id=pattern_id,
            step_index=note.step_index,
            pitch=note.pitch,
            velocity=note.velocity,
        )
        db.add(db_note)
        db_notes.append(db_note)

    db.commit()
    for db_note in db_notes:
        db.refresh(db_note)

    return [model_to_note(n) for n in db_notes]
