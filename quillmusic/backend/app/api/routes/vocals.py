"""
Vocals API routes for ElevenLabs TTS integration
"""
import io
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, constr

from app.core.config import settings
from app.providers.elevenlabs_tts import ElevenLabsClient, ElevenLabsTTSError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vocals", tags=["vocals"])


class VocalPreviewRequest(BaseModel):
    """Request schema for vocal preview generation."""

    text: constr(min_length=1, max_length=5000) = Field(
        ...,
        description="Text or lyrics to convert to speech"
    )
    voice_id: constr(min_length=1) = Field(
        ...,
        description="ElevenLabs voice ID"
    )
    model_id: Optional[str] = Field(
        None,
        description="ElevenLabs model ID (optional, defaults to server config)"
    )


@router.post("/preview")
async def preview_vocals(payload: VocalPreviewRequest) -> StreamingResponse:
    """
    Generate a vocal preview using ElevenLabs TTS.

    This endpoint takes text/lyrics and a voice ID, calls the ElevenLabs API,
    and streams back the generated audio as MP3.

    Args:
        payload: Vocal preview request with text, voice_id, and optional model_id

    Returns:
        StreamingResponse with audio/mpeg content

    Raises:
        HTTPException: If ElevenLabs API is not configured or if generation fails
    """
    # Check if ElevenLabs is configured
    if not settings.ELEVENLABS_API_KEY:
        logger.error("ElevenLabs API key not configured")
        raise HTTPException(
            status_code=500,
            detail="ElevenLabs API key not configured. Please set QUILLMUSIC_ELEVENLABS_API_KEY."
        )

    # Create client
    client = ElevenLabsClient(
        api_key=settings.ELEVENLABS_API_KEY,
        base_url=settings.ELEVENLABS_BASE_URL,
        default_model=settings.ELEVENLABS_DEFAULT_MODEL,
    )

    # Generate speech
    try:
        logger.info(
            f"Generating vocal preview: voice_id={payload.voice_id}, "
            f"model={payload.model_id or settings.ELEVENLABS_DEFAULT_MODEL}, "
            f"text_length={len(payload.text)}"
        )

        audio_bytes = await client.generate_speech(
            text=payload.text,
            voice_id=payload.voice_id,
            model_id=payload.model_id,
        )

        # Stream audio back to client
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="vocal-preview.mp3"',
            },
        )

    except ElevenLabsTTSError as exc:
        logger.error(f"ElevenLabs TTS error: {exc}")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to generate vocals: {str(exc)}"
        )
    except Exception as exc:
        logger.error(f"Unexpected error in vocal preview: {exc}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating vocals"
        )
