"""
Replicate MusicGen client for hosted audio generation.

This module provides integration with Replicate's hosted MusicGen model
for generating music using their predictions API.

API Documentation: https://replicate.com/docs/reference/http
"""
import logging
import asyncio
from typing import Optional
import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


class ReplicateMusicGenError(Exception):
    """Raised when Replicate MusicGen API request fails."""
    pass


class ReplicateMusicGenClient:
    """Client for Replicate MusicGen API."""

    def __init__(self, settings: Settings):
        """
        Initialize Replicate MusicGen client.

        Args:
            settings: Application settings containing Replicate configuration
        """
        self.settings = settings
        self.base_url = settings.REPLICATE_BASE_URL.rstrip("/")
        self.api_token = settings.REPLICATE_API_TOKEN
        self.version = settings.REPLICATE_MUSICGEN_VERSION

        if not self.api_token:
            raise ReplicateMusicGenError("Replicate API token is not configured")

        if not self.version:
            raise ReplicateMusicGenError("Replicate MusicGen version is not configured")

        logger.info(f"ReplicateMusicGenClient initialized with base_url: {self.base_url}")

    async def generate_audio(
        self,
        prompt: str,
        duration_seconds: Optional[int] = None,
        poll_interval: float = 1.0,
        timeout: float = 90.0,
    ) -> str:
        """
        Generate audio using Replicate's MusicGen model.

        This method:
        1. Creates a prediction via POST /v1/predictions
        2. Polls GET /v1/predictions/{id} until succeeded/failed
        3. Returns the audio URL from the prediction output

        Args:
            prompt: Text description of the music to generate
            duration_seconds: Desired duration in seconds (default: 30)
            poll_interval: Seconds to wait between polls (default: 1.0)
            timeout: Maximum seconds to wait for completion (default: 90.0)

        Returns:
            Public URL string to the generated audio file

        Raises:
            ReplicateMusicGenError: If API request fails, times out, or returns invalid response
        """
        if duration_seconds is None:
            duration_seconds = 30

        # Build request payload for prediction creation
        payload = {
            "version": self.version,
            "input": {
                "prompt": prompt,
                "duration": duration_seconds,
            }
        }

        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
        }

        logger.info(f"Creating Replicate prediction: prompt='{prompt}', duration={duration_seconds}s")

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Step 1: Create prediction
                create_url = f"{self.base_url}/v1/predictions"
                response = await client.post(create_url, headers=headers, json=payload)

                if response.status_code != 201:
                    error_msg = f"Replicate API returned status {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise ReplicateMusicGenError(error_msg)

                try:
                    prediction = response.json()
                except Exception as parse_err:
                    error_msg = f"Failed to parse Replicate API response as JSON: {parse_err}"
                    logger.error(error_msg)
                    raise ReplicateMusicGenError(error_msg) from parse_err

                prediction_id = prediction.get("id")
                if not prediction_id:
                    error_msg = f"Replicate API response missing 'id' field: {prediction}"
                    logger.error(error_msg)
                    raise ReplicateMusicGenError(error_msg)

                logger.info(f"Created prediction {prediction_id}, status: {prediction.get('status')}")

                # Step 2: Poll for completion
                start_time = asyncio.get_event_loop().time()
                get_url = f"{self.base_url}/v1/predictions/{prediction_id}"

                while True:
                    # Check timeout
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed > timeout:
                        error_msg = f"Replicate prediction {prediction_id} timed out after {timeout}s"
                        logger.error(error_msg)
                        raise ReplicateMusicGenError(error_msg)

                    # Poll prediction status
                    poll_response = await client.get(get_url, headers=headers)

                    if poll_response.status_code != 200:
                        error_msg = f"Replicate API poll returned status {poll_response.status_code}: {poll_response.text}"
                        logger.error(error_msg)
                        raise ReplicateMusicGenError(error_msg)

                    try:
                        prediction = poll_response.json()
                    except Exception as parse_err:
                        error_msg = f"Failed to parse Replicate poll response as JSON: {parse_err}"
                        logger.error(error_msg)
                        raise ReplicateMusicGenError(error_msg) from parse_err

                    status = prediction.get("status")
                    logger.debug(f"Prediction {prediction_id} status: {status}")

                    if status == "succeeded":
                        # Extract audio URL from output
                        output = prediction.get("output")
                        if not output:
                            error_msg = f"Replicate prediction succeeded but output is empty: {prediction}"
                            logger.error(error_msg)
                            raise ReplicateMusicGenError(error_msg)

                        # Output can be a string URL or a list with a URL
                        if isinstance(output, str):
                            audio_url = output
                        elif isinstance(output, list) and len(output) > 0:
                            audio_url = output[0]
                        else:
                            error_msg = f"Replicate prediction output has unexpected format: {output}"
                            logger.error(error_msg)
                            raise ReplicateMusicGenError(error_msg)

                        logger.info(f"Replicate prediction succeeded: {audio_url}")
                        return audio_url

                    elif status in ["failed", "canceled"]:
                        error = prediction.get("error", "Unknown error")
                        error_msg = f"Replicate prediction {status}: {error}"
                        logger.error(error_msg)
                        raise ReplicateMusicGenError(error_msg)

                    elif status in ["starting", "processing"]:
                        # Continue polling
                        await asyncio.sleep(poll_interval)
                        continue

                    else:
                        # Unknown status - treat as error
                        error_msg = f"Replicate prediction has unknown status: {status}"
                        logger.error(error_msg)
                        raise ReplicateMusicGenError(error_msg)

        except httpx.HTTPError as http_err:
            error_msg = f"HTTP error calling Replicate API: {http_err}"
            logger.error(error_msg)
            raise ReplicateMusicGenError(error_msg) from http_err
        except ReplicateMusicGenError:
            # Re-raise our custom errors
            raise
        except Exception as exc:
            error_msg = f"Unexpected error calling Replicate API: {exc}"
            logger.error(error_msg)
            raise ReplicateMusicGenError(error_msg) from exc
