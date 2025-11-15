"""
Song Blueprint API endpoints
"""
import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.song import SongBlueprintRequest, SongBlueprintResponse
from app.services.song_blueprint_service import SongBlueprintEngine
from app.core.dependencies import get_song_blueprint_engine
from app.core.database import get_db
from app.models.blueprint import SongBlueprintModel

router = APIRouter()


@router.post("/song/blueprint", response_model=SongBlueprintResponse)
async def create_song_blueprint(
    request: SongBlueprintRequest,
    engine: SongBlueprintEngine = Depends(get_song_blueprint_engine),
    db: Session = Depends(get_db),
):
    """
    Generate a song blueprint from a high-level description.

    This endpoint takes a prompt, genre, mood, and optional parameters,
    and returns a complete song structure with sections, lyrics, and
    vocal style configuration.

    The engine used (fake or LLM-powered) depends on the SONG_ENGINE_MODE
    configuration setting.

    The generated blueprint is stored in the database for later use in
    instrumental rendering.
    """
    try:
        blueprint = engine.generate_blueprint(request)

        # Store blueprint in database for instrumental rendering
        blueprint_model = SongBlueprintModel(
            id=blueprint.song_id,
            title=blueprint.title,
            genre=blueprint.genre,
            mood=blueprint.mood,
            bpm=blueprint.bpm,
            key=blueprint.key,
            blueprint_json=json.dumps(blueprint.model_dump()),
        )
        db.add(blueprint_model)
        db.commit()

        return blueprint
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate blueprint: {str(e)}",
        )


@router.get("/song/blueprints", response_model=list[SongBlueprintResponse])
async def list_blueprints(
    db: Session = Depends(get_db),
    limit: int = 20,
):
    """
    List recently generated song blueprints.

    This allows users to see their previously generated blueprints
    for use in the Instrumental Studio.
    """
    try:
        blueprints = db.query(SongBlueprintModel).order_by(
            SongBlueprintModel.created_at.desc()
        ).limit(limit).all()

        return [
            SongBlueprintResponse(**json.loads(bp.blueprint_json))
            for bp in blueprints
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list blueprints: {str(e)}",
        )


@router.get("/song/blueprints/{blueprint_id}", response_model=SongBlueprintResponse)
async def get_blueprint(
    blueprint_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific blueprint by ID."""
    try:
        blueprint = db.query(SongBlueprintModel).filter(
            SongBlueprintModel.id == blueprint_id
        ).first()

        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")

        return SongBlueprintResponse(**json.loads(blueprint.blueprint_json))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get blueprint: {str(e)}",
        )
