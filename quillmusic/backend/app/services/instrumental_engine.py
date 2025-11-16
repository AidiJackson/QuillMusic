"""
Instrumental engine abstraction for rendering audio from blueprints and manual projects
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional
import logging
import httpx
import asyncio

from app.core.config import InstrumentalEngineConfig

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when audio provider configuration is invalid or missing."""
    pass


class ExternalAudioError(Exception):
    """Raised when external audio provider returns an error."""
    pass


class BaseInstrumentalEngine(ABC):
    """Abstract base class for instrumental engines."""

    @abstractmethod
    def render_from_blueprint(self, blueprint) -> Tuple[str, int]:
        """
        Render instrumental from a song blueprint.

        Args:
            blueprint: SongBlueprintResponse object

        Returns:
            Tuple of (audio_url, duration_seconds)
        """
        pass

    @abstractmethod
    def render_from_manual_project(self, project, tracks, patterns) -> Tuple[str, int]:
        """
        Render instrumental from a manual project.

        Args:
            project: ManualProject object
            tracks: List of Track objects
            patterns: List of Pattern objects

        Returns:
            Tuple of (audio_url, duration_seconds)
        """
        pass


class FakeInstrumentalEngine(BaseInstrumentalEngine):
    """Fake instrumental engine for development and testing."""

    def render_from_blueprint(self, blueprint) -> Tuple[str, int]:
        """
        Generate fake instrumental from blueprint.

        Calculates duration based on sections and tempo.
        """
        logger.info(f"FakeInstrumentalEngine: Rendering from blueprint {blueprint.song_id}")

        # Calculate duration based on sections
        total_bars = sum(section.bars for section in blueprint.sections)

        # Calculate duration: bars * (60 / bpm) * 4 (assuming 4/4 time)
        # This gives us seconds per bar, multiplied by number of bars
        seconds_per_bar = (60.0 / blueprint.bpm) * 4
        duration_seconds = int(total_bars * seconds_per_bar)

        # Clamp to reasonable range
        duration_seconds = max(8, min(duration_seconds, 600))

        # Generate fake audio URL
        audio_url = f"/audio/fake-instrumental/blueprint-{blueprint.song_id}.mp3"

        logger.info(f"Generated fake instrumental: {audio_url}, duration: {duration_seconds}s")
        return audio_url, duration_seconds

    def render_from_manual_project(self, project, tracks, patterns) -> Tuple[str, int]:
        """
        Generate fake instrumental from manual project.

        Calculates duration based on patterns and tempo.
        """
        logger.info(f"FakeInstrumentalEngine: Rendering from manual project {project.id}")

        # Find the last bar position across all patterns
        last_bar = 0
        if patterns:
            for pattern in patterns:
                pattern_end = pattern.start_bar + pattern.length_bars
                last_bar = max(last_bar, pattern_end)

        # If no patterns, use a default length
        if last_bar == 0:
            last_bar = 16  # Default to 16 bars

        # Calculate duration: bars * (60 / bpm) * 4 (assuming 4/4 time)
        seconds_per_bar = (60.0 / project.tempo_bpm) * 4
        duration_seconds = int(last_bar * seconds_per_bar)

        # Clamp to reasonable range
        duration_seconds = max(8, min(duration_seconds, 600))

        # Generate fake audio URL
        audio_url = f"/audio/fake-instrumental/manual-{project.id}.mp3"

        logger.info(f"Generated fake instrumental: {audio_url}, duration: {duration_seconds}s")
        return audio_url, duration_seconds


class ExternalInstrumentalEngine(BaseInstrumentalEngine):
    """External HTTP-based instrumental engine for real audio generation."""

    def __init__(self, engine_config: InstrumentalEngineConfig):
        """
        Initialize external instrumental engine.

        Args:
            engine_config: Engine configuration with base_url, api_key, model, and name
        """
        self.engine_config = engine_config
        self.engine_name = engine_config.name
        logger.info(f"ExternalInstrumentalEngine initialized: {self.engine_name} ({engine_config.base_url})")

    def _build_prompt_from_blueprint(self, blueprint) -> str:
        """
        Build a text prompt from a song blueprint for audio generation.

        Args:
            blueprint: SongBlueprintResponse object

        Returns:
            Prompt string for audio generation
        """
        # Build a descriptive prompt from blueprint metadata
        parts = []

        if blueprint.genre:
            parts.append(f"{blueprint.genre} genre")

        if blueprint.mood:
            parts.append(f"{blueprint.mood} mood")

        parts.append(f"{blueprint.bpm} BPM")

        if blueprint.key:
            parts.append(f"in {blueprint.key}")

        # Add section structure info
        if blueprint.sections:
            section_names = [s.name for s in blueprint.sections]
            parts.append(f"with sections: {', '.join(section_names)}")

        prompt = "Instrumental music: " + ", ".join(parts)
        logger.info(f"Built prompt from blueprint: {prompt}")
        return prompt

    def _build_prompt_from_manual_project(self, project, tracks, patterns) -> str:
        """
        Build a text prompt from a manual project for audio generation.

        Args:
            project: ManualProject object
            tracks: List of Track objects
            patterns: List of Pattern objects

        Returns:
            Prompt string for audio generation
        """
        # Build a descriptive prompt from manual project metadata
        parts = []

        parts.append(f"{project.tempo_bpm} BPM")

        if project.key:
            parts.append(f"in {project.key}")

        # Add instrument types from tracks
        if tracks:
            instruments = list(set(track.instrument_type for track in tracks))
            if instruments:
                parts.append(f"with instruments: {', '.join(instruments)}")

        # Add pattern count info
        if patterns:
            parts.append(f"{len(patterns)} patterns")

        prompt = "Instrumental music: " + ", ".join(parts)
        logger.info(f"Built prompt from manual project: {prompt}")
        return prompt

    def _infer_duration_from_blueprint(self, blueprint) -> int:
        """
        Calculate expected duration from blueprint.

        Args:
            blueprint: SongBlueprintResponse object

        Returns:
            Duration in seconds
        """
        total_bars = sum(section.bars for section in blueprint.sections)
        seconds_per_bar = (60.0 / blueprint.bpm) * 4
        duration_seconds = int(total_bars * seconds_per_bar)
        duration_seconds = max(8, min(duration_seconds, 600))
        return duration_seconds

    def _infer_duration_from_manual_project(self, project, patterns) -> int:
        """
        Calculate expected duration from manual project.

        Args:
            project: ManualProject object
            patterns: List of Pattern objects

        Returns:
            Duration in seconds
        """
        last_bar = 0
        if patterns:
            for pattern in patterns:
                pattern_end = pattern.start_bar + pattern.length_bars
                last_bar = max(last_bar, pattern_end)

        if last_bar == 0:
            last_bar = 16  # Default to 16 bars

        seconds_per_bar = (60.0 / project.tempo_bpm) * 4
        duration_seconds = int(last_bar * seconds_per_bar)
        duration_seconds = max(8, min(duration_seconds, 600))
        return duration_seconds

    def _post_generate(self, prompt: str, duration_seconds: int) -> Tuple[str, int]:
        """
        Make HTTP request to external audio generation API.

        Routes to the appropriate client based on engine name:
        - stable_audio_api: Official Stable Audio hosted API
        - stable_audio_open: Self-hosted Stable Audio Open
        - musicgen: Self-hosted MusicGen
        - Others: Generic HTTP endpoint

        Args:
            prompt: Text prompt for audio generation
            duration_seconds: Desired duration in seconds

        Returns:
            Tuple of (audio_url, duration_seconds)

        Raises:
            ExternalAudioError: If API request fails or returns invalid response
        """
        # Route to specific client based on engine name
        if self.engine_name == "stable_audio_api":
            # Use dedicated Stable Audio API client
            from app.providers.stable_audio_api import generate_stable_audio, StableAudioAPIError
            try:
                # Run async function in sync context
                audio_url = asyncio.run(generate_stable_audio(
                    engine_config=self.engine_config,
                    prompt=prompt,
                    duration_seconds=duration_seconds,
                ))
                return (audio_url, duration_seconds)
            except StableAudioAPIError as exc:
                logger.error(f"Stable Audio API error: {exc}")
                raise ExternalAudioError(f"Stable Audio API request failed: {exc}") from exc

        # For other engines (stable_audio_open, musicgen), use generic HTTP client
        # This maintains backward compatibility with existing external engines
        else:
            return self._generic_http_generate(prompt, duration_seconds)

    def _generic_http_generate(self, prompt: str, duration_seconds: int) -> Tuple[str, int]:
        """
        Generic HTTP client for external audio generation APIs.

        This method provides a generic implementation for external engines
        that follow a similar HTTP interface pattern.

        Args:
            prompt: Text prompt for audio generation
            duration_seconds: Desired duration in seconds

        Returns:
            Tuple of (audio_url, duration_seconds)

        Raises:
            ExternalAudioError: If API request fails or returns invalid response
        """
        if not self.engine_config.base_url:
            raise ExternalAudioError(f"Engine {self.engine_name} missing base_url configuration")

        try:
            base_url = self.engine_config.base_url.rstrip("/")

            # Use appropriate endpoint path based on engine
            if self.engine_name == "musicgen":
                url = f"{base_url}/v1/generate/audio"
            else:
                url = f"{base_url}/v2/generate/audio"

            model = self.engine_config.model or "default-model"

            logger.info(f"Calling external audio API ({self.engine_name}): {url}")
            logger.info(f"Model: {model}, Prompt: {prompt}, Duration: {duration_seconds}s")

            headers = {
                "Content-Type": "application/json",
            }

            # Add authorization if API key is configured
            if self.engine_config.api_key:
                headers["Authorization"] = f"Bearer {self.engine_config.api_key}"

            response = httpx.post(
                url,
                headers=headers,
                json={
                    "model": model,
                    "prompt": prompt,
                    "seconds_total": duration_seconds,
                },
                timeout=120.0,
            )

            if response.status_code != 200:
                error_msg = f"Audio API returned status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise ExternalAudioError(error_msg)

            data = response.json()

            # Check for successful response
            if data.get("status") == "ready" and data.get("audio_url"):
                audio_url = data["audio_url"]
                logger.info(f"External audio generated successfully: {audio_url}")
                return (audio_url, duration_seconds)
            else:
                error_msg = f"Audio API returned unexpected response: {data}"
                logger.error(error_msg)
                raise ExternalAudioError(error_msg)

        except httpx.HTTPError as exc:
            error_msg = f"HTTP error calling audio API: {exc}"
            logger.error(error_msg)
            raise ExternalAudioError(error_msg) from exc
        except Exception as exc:
            error_msg = f"Unexpected error calling audio API: {exc}"
            logger.error(error_msg)
            raise ExternalAudioError(error_msg) from exc

    def render_from_blueprint(self, blueprint) -> Tuple[str, int]:
        """
        Render instrumental from a song blueprint using external API.

        Args:
            blueprint: SongBlueprintResponse object

        Returns:
            Tuple of (audio_url, duration_seconds)
        """
        logger.info(f"ExternalInstrumentalEngine: Rendering from blueprint {blueprint.song_id}")
        prompt = self._build_prompt_from_blueprint(blueprint)
        duration_seconds = self._infer_duration_from_blueprint(blueprint)
        return self._post_generate(prompt, duration_seconds)

    def render_from_manual_project(self, project, tracks, patterns) -> Tuple[str, int]:
        """
        Render instrumental from a manual project using external API.

        Args:
            project: ManualProject object
            tracks: List of Track objects
            patterns: List of Pattern objects

        Returns:
            Tuple of (audio_url, duration_seconds)
        """
        logger.info(f"ExternalInstrumentalEngine: Rendering from manual project {project.id}")
        prompt = self._build_prompt_from_manual_project(project, tracks, patterns)
        duration_seconds = self._infer_duration_from_manual_project(project, patterns)
        return self._post_generate(prompt, duration_seconds)


class HttpInstrumentalEngine(BaseInstrumentalEngine):
    """
    HTTP-based instrumental engine for external API integration.

    This is a placeholder for future real model integration (Stable Audio, MusicGen, etc.).
    For now, it delegates to FakeInstrumentalEngine.
    """

    def __init__(self):
        self._fake_engine = FakeInstrumentalEngine()
        logger.warning("HttpInstrumentalEngine is using FakeInstrumentalEngine internally (not yet implemented)")

    def render_from_blueprint(self, blueprint) -> Tuple[str, int]:
        """
        Placeholder for HTTP-based rendering from blueprint.

        In a future phase, this will:
        1. Convert blueprint to prompt/conditioning for external API
        2. Make HTTP request to external model (Stable Audio / MusicGen)
        3. Download and store the resulting audio
        4. Return the stored audio URL

        For now, delegates to fake engine.
        """
        logger.info("HttpInstrumentalEngine.render_from_blueprint: Delegating to fake engine (future: real API call)")
        return self._fake_engine.render_from_blueprint(blueprint)

    def render_from_manual_project(self, project, tracks, patterns) -> Tuple[str, int]:
        """
        Placeholder for HTTP-based rendering from manual project.

        In a future phase, this will:
        1. Convert manual project to MIDI or audio conditioning
        2. Make HTTP request to external model
        3. Download and store the resulting audio
        4. Return the stored audio URL

        For now, delegates to fake engine.
        """
        logger.info("HttpInstrumentalEngine.render_from_manual_project: Delegating to fake engine (future: real API call)")
        return self._fake_engine.render_from_manual_project(project, tracks, patterns)


def get_instrumental_engine(
    engine_type: str,
    model: Optional[str] = None,
    settings=None
) -> BaseInstrumentalEngine:
    """
    Factory function to get the appropriate instrumental engine.

    Args:
        engine_type: "fake" or "external_http"
        model: Engine name/model identifier (e.g., "stable_audio_api", "musicgen")
        settings: Settings object (optional)

    Returns:
        BaseInstrumentalEngine instance

    Raises:
        ConfigurationError: If external_http is requested but configuration is invalid
    """
    if engine_type == "fake":
        return FakeInstrumentalEngine()
    elif engine_type == "external_http":
        # Check if settings are provided
        if settings is None:
            from app.core.config import settings as default_settings
            settings = default_settings

        # Determine which engine to use based on model parameter
        # Model should be the engine name (e.g., "stable_audio_api", "musicgen")
        engine_name = model or "stable_audio_api"

        # Get engine configuration
        engine_config = settings.get_engine_config(engine_name)

        if engine_config is None:
            raise ConfigurationError(
                f"Engine '{engine_name}' is not configured. "
                f"Available engines: {[e.name for e in settings.instrumental_engines]}"
            )

        if engine_config.engine_type != "external_http":
            raise ConfigurationError(
                f"Engine '{engine_name}' is configured as '{engine_config.engine_type}', "
                f"but 'external_http' was requested"
            )

        # Validate that base_url is configured for external engines
        if not engine_config.base_url:
            raise ConfigurationError(
                f"Engine '{engine_name}' is missing base_url configuration"
            )

        # Create external engine with configuration
        return ExternalInstrumentalEngine(engine_config=engine_config)
    else:
        logger.warning(f"Unknown engine type '{engine_type}', defaulting to fake")
        return FakeInstrumentalEngine()
