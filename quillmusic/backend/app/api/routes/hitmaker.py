"""
HitMaker API routes for song analysis and AI-driven improvement suggestions.
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.blueprint import SongBlueprintModel
from app.models.manual import ManualProjectModel
from app.schemas.hitmaker import (
    HitMakerAnalysis,
    HitMakerInfluenceRequest,
    HitMakerInfluenceResponse,
)
from app.schemas.song import SongBlueprintResponse
from app.services.hitmaker_engine import HitMakerEngine

router = APIRouter()


@router.post("/analyze/blueprint", response_model=HitMakerAnalysis)
def analyze_blueprint(
    blueprint_id: str,
    db: Session = Depends(get_db),
):
    """
    Analyze an AI-generated song blueprint for hit potential.

    Returns DNA profile, HitScore breakdown, and actionable insights.
    """
    # Load blueprint from database
    blueprint_model = db.query(SongBlueprintModel).filter(
        SongBlueprintModel.id == blueprint_id
    ).first()

    if not blueprint_model:
        raise HTTPException(status_code=404, detail=f"Blueprint {blueprint_id} not found")

    # Parse blueprint JSON
    blueprint_data = json.loads(blueprint_model.blueprint_json)
    blueprint = SongBlueprintResponse(**blueprint_data)

    # Analyze
    engine = HitMakerEngine()
    analysis = engine.analyze_blueprint(blueprint)

    return analysis


@router.post("/analyze/manual", response_model=HitMakerAnalysis)
def analyze_manual_project(
    manual_project_id: str,
    db: Session = Depends(get_db),
):
    """
    Analyze a Manual Creator project for hit potential.

    Returns DNA profile, HitScore breakdown, and actionable insights.
    """
    # Load project with all relations
    project = db.query(ManualProjectModel).filter(
        ManualProjectModel.id == manual_project_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail=f"Manual project {manual_project_id} not found")

    # Analyze
    engine = HitMakerEngine()
    analysis = engine.analyze_manual_project(project)

    return analysis


@router.post("/influence/blueprint", response_model=HitMakerInfluenceResponse)
def apply_influences_to_blueprint(
    request: HitMakerInfluenceRequest,
    db: Session = Depends(get_db),
):
    """
    Apply artistic influences to an AI blueprint.

    Returns adjusted DNA and creative suggestions for hooks, chorus,
    structure, instrumentation, and vocal style.
    """
    if not request.source_blueprint_id:
        raise HTTPException(status_code=400, detail="source_blueprint_id is required")

    # Load blueprint
    blueprint_model = db.query(SongBlueprintModel).filter(
        SongBlueprintModel.id == request.source_blueprint_id
    ).first()

    if not blueprint_model:
        raise HTTPException(
            status_code=404,
            detail=f"Blueprint {request.source_blueprint_id} not found"
        )

    # Parse blueprint
    blueprint_data = json.loads(blueprint_model.blueprint_json)
    blueprint = SongBlueprintResponse(**blueprint_data)

    # Validate influences
    total_weight = sum(inf.weight for inf in request.influences)
    if total_weight > 1.2:
        raise HTTPException(
            status_code=400,
            detail=f"Total influence weight {total_weight:.2f} exceeds 1.2"
        )

    # Apply influences
    engine = HitMakerEngine()
    response = engine.apply_influences_to_blueprint(
        blueprint,
        request.influences,
        request.target_mood,
        request.target_genre,
    )

    return response


@router.post("/influence/manual", response_model=HitMakerInfluenceResponse)
def apply_influences_to_manual(
    request: HitMakerInfluenceRequest,
    db: Session = Depends(get_db),
):
    """
    Apply artistic influences to a Manual Creator project.

    Returns adjusted DNA and creative suggestions for hooks, chorus,
    structure, instrumentation, and vocal style.
    """
    if not request.source_manual_project_id:
        raise HTTPException(status_code=400, detail="source_manual_project_id is required")

    # Load project
    project = db.query(ManualProjectModel).filter(
        ManualProjectModel.id == request.source_manual_project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Manual project {request.source_manual_project_id} not found"
        )

    # Validate influences
    total_weight = sum(inf.weight for inf in request.influences)
    if total_weight > 1.2:
        raise HTTPException(
            status_code=400,
            detail=f"Total influence weight {total_weight:.2f} exceeds 1.2"
        )

    # Apply influences
    engine = HitMakerEngine()
    response = engine.apply_influences_to_project(
        project,
        request.influences,
        request.target_mood,
        request.target_genre,
    )

    return response
