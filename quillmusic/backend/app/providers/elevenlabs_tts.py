"""
ElevenLabs Text-to-Speech provider for vocal generation.

This module provides integration with the ElevenLabs API for generating
high-quality AI vocals from text.

API Documentation: https://elevenlabs.io/docs/api-reference/text-to-speech
"""
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


class ElevenLabsTTSError(Exception):
    """Raised when ElevenLabs TTS API request fails."""
    pass


class ElevenLabsClient:
    """Client for ElevenLabs Text-to-Speech API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.elevenlabs.io",
        default_model: str = "eleven_turbo_v2_5",
    ):
        """
        Initialize ElevenLabs TTS client.

        Args:
            api_key: ElevenLabs API key
            base_url: Base URL for ElevenLabs API
            default_model: Default model ID to use for TTS
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        model_id: Optional[str] = None,
    ) -> bytes:
        """
        Generate speech audio from text using ElevenLabs TTS.

        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            model_id: Optional model ID (defaults to client's default_model)

        Returns:
            Audio bytes (MP3 format)

        Raises:
            ElevenLabsTTSError: If API request fails
        """
        if not text or not text.strip():
            raise ElevenLabsTTSError("Text cannot be empty")

        if not voice_id or not voice_id.strip():
            raise ElevenLabsTTSError("Voice ID cannot be empty")

        # Build request URL
        url = f"{self.base_url}/v1/text-to-speech/{voice_id}"

        # Use provided model or fallback to default
        model = model_id or self.default_model

        # Build request payload
        payload = {
            "model_id": model,
            "text": text,
        }

        logger.info(f"Calling ElevenLabs TTS API: {url}")
        logger.info(f"Voice ID: {voice_id}, Model: {model}, Text length: {len(text)} chars")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers={
                        "xi-api-key": self.api_key,
                        "Content-Type": "application/json",
                        "Accept": "audio/mpeg",
                    },
                    json=payload,
                )

                # Check HTTP status
                if response.status_code != 200:
                    error_text = response.text[:200] if response.text else "No error details"
                    error_msg = f"ElevenLabs API returned status {response.status_code}: {error_text}"
                    logger.error(error_msg)
                    raise ElevenLabsTTSError(error_msg)

                # Return audio bytes
                audio_bytes = response.content
                logger.info(f"ElevenLabs TTS succeeded: {len(audio_bytes)} bytes generated")
                return audio_bytes

        except httpx.HTTPError as http_err:
            error_msg = f"HTTP error calling ElevenLabs API: {http_err}"
            logger.error(error_msg)
            raise ElevenLabsTTSError(error_msg) from http_err
        except ElevenLabsTTSError:
            # Re-raise our custom errors
            raise
        except Exception as exc:
            error_msg = f"Unexpected error calling ElevenLabs API: {exc}"
            logger.error(error_msg)
            raise ElevenLabsTTSError(error_msg) from exc
