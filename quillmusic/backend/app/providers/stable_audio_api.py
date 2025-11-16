"""
Stable Audio API client for hosted audio generation.

This module provides integration with the official Stable Audio API
for generating high-quality music using hosted models.

API Documentation: https://stability.ai/stable-audio
"""
import logging
from typing import Optional
import httpx

from app.core.config import InstrumentalEngineConfig

logger = logging.getLogger(__name__)


class StableAudioAPIError(Exception):
    """Raised when Stable Audio API request fails."""
    pass


async def generate_stable_audio(
    engine_config: InstrumentalEngineConfig,
    prompt: str,
    duration_seconds: Optional[int] = None,
) -> str:
    """
    Call Stable Audio hosted API to generate music.

    This function implements the Stable Audio V2-like HTTP interface:
    - Endpoint: POST {BASE_URL}/v2/generate/audio
    - Headers: Authorization: Bearer {API_KEY}
    - Body: { "model": "...", "prompt": "...", "seconds_total": 30 }
    - Response: { "status": "ready", "audio_url": "https://..." }

    Note: This is a simplified implementation based on the expected API shape.
    The founder should verify against actual Stable Audio API documentation
    and adjust as needed.

    Args:
        engine_config: Engine configuration with base_url, api_key, model
        prompt: Text description of the music to generate
        duration_seconds: Desired duration in seconds (default: 30)

    Returns:
        Public URL string to the generated audio file

    Raises:
        StableAudioAPIError: If API request fails or returns invalid response
    """
    if not engine_config.base_url:
        raise StableAudioAPIError("Stable Audio API base_url is not configured")

    if not engine_config.api_key:
        raise StableAudioAPIError("Stable Audio API api_key is not configured")

    # Build request URL
    url = engine_config.base_url.rstrip("/") + "/v2/generate/audio"

    # Use configured model or fallback to default
    model = engine_config.model or "stable-audio-1.0"

    # Default duration if not specified
    if duration_seconds is None:
        duration_seconds = 30

    # Build request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "seconds_total": duration_seconds,
    }

    logger.info(f"Calling Stable Audio API: {url}")
    logger.info(f"Model: {model}, Prompt: {prompt}, Duration: {duration_seconds}s")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {engine_config.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            # Check HTTP status
            if response.status_code != 200:
                error_msg = f"Stable Audio API returned status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise StableAudioAPIError(error_msg)

            # Parse JSON response
            try:
                data = response.json()
            except Exception as parse_err:
                error_msg = f"Failed to parse Stable Audio API response as JSON: {parse_err}"
                logger.error(error_msg)
                raise StableAudioAPIError(error_msg) from parse_err

            # Extract audio URL
            if data.get("status") == "ready" and data.get("audio_url"):
                audio_url = data["audio_url"]
                logger.info(f"Stable Audio API succeeded: {audio_url}")
                return audio_url
            else:
                error_msg = f"Stable Audio API returned unexpected response: {data}"
                logger.error(error_msg)
                raise StableAudioAPIError(error_msg)

    except httpx.HTTPError as http_err:
        error_msg = f"HTTP error calling Stable Audio API: {http_err}"
        logger.error(error_msg)
        raise StableAudioAPIError(error_msg) from http_err
    except StableAudioAPIError:
        # Re-raise our custom errors
        raise
    except Exception as exc:
        error_msg = f"Unexpected error calling Stable Audio API: {exc}"
        logger.error(error_msg)
        raise StableAudioAPIError(error_msg) from exc
