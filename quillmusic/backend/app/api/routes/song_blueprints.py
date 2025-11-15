"""
Song Blueprint API endpoints
"""
from fastapi import APIRouter, HTTPException

from app.schemas.song import SongBlueprintRequest, SongBlueprintResponse
from app.services.song_blueprint_service import get_blueprint_engine

router = APIRouter()


@router.post("/song/blueprint", response_model=SongBlueprintResponse)
async def create_song_blueprint(request: SongBlueprintRequest):
    """
    Generate a song blueprint from a high-level description.

    This endpoint takes a prompt, genre, mood, and optional parameters,
    and returns a complete song structure with sections, lyrics, and
    vocal style configuration.
    """
    try:
        engine = get_blueprint_engine()
        blueprint = engine.generate_blueprint(request)
        return blueprint
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate blueprint: {str(e)}",
        )
