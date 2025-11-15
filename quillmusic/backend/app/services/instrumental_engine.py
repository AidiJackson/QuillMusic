"""
Instrumental engine abstraction for rendering audio from blueprints and manual projects
"""
from abc import ABC, abstractmethod
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


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


def get_instrumental_engine(engine_type: str) -> BaseInstrumentalEngine:
    """
    Factory function to get the appropriate instrumental engine.

    Args:
        engine_type: "fake" or "external_http"

    Returns:
        BaseInstrumentalEngine instance
    """
    if engine_type == "fake":
        return FakeInstrumentalEngine()
    elif engine_type == "external_http":
        return HttpInstrumentalEngine()
    else:
        logger.warning(f"Unknown engine type '{engine_type}', defaulting to fake")
        return FakeInstrumentalEngine()
