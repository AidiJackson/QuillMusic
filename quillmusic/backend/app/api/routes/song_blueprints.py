"""
Song Blueprint API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends

from app.schemas.song import SongBlueprintRequest, SongBlueprintResponse
from app.services.song_blueprint_service import SongBlueprintEngine
from app.core.dependencies import get_song_blueprint_engine

router = APIRouter()


@router.post("/song/blueprint", response_model=SongBlueprintResponse)
async def create_song_blueprint(
    request: SongBlueprintRequest,
    engine: SongBlueprintEngine = Depends(get_song_blueprint_engine),
):
    """
    Generate a song blueprint from a high-level description.

    This endpoint takes a prompt, genre, mood, and optional parameters,
    and returns a complete song structure with sections, lyrics, and
    vocal style configuration.

    The engine used (fake or LLM-powered) depends on the SONG_ENGINE_MODE
    configuration setting.
    """
    try:
        blueprint = engine.generate_blueprint(request)
        return blueprint
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate blueprint: {str(e)}",
        )
