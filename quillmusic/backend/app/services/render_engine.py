"""
Render Engine Service

This module contains engines for rendering audio (instrumental, vocals, full mix).
Currently implements a fake/mock engine for development and testing.
"""
import uuid
from abc import ABC, abstractmethod
from typing import Dict

from app.schemas.render import RenderJobStatus, RenderType, RenderStatus


class RenderEngine(ABC):
    """Abstract base class for render engines."""

    @abstractmethod
    def submit(self, song_id: str, render_type: RenderType) -> str:
        """Submit a render job and return job_id."""
        pass

    @abstractmethod
    def status(self, job_id: str) -> RenderJobStatus:
        """Get status of a render job."""
        pass


class FakeRenderEngine(RenderEngine):
    """
    Fake render engine for development and testing.

    Immediately returns "ready" status with demo audio URLs.
    In production, this would submit to a job queue and process asynchronously.
    """

    def __init__(self):
        """Initialize the fake render engine."""
        # In-memory job store (in production this would be Redis/DB)
        self._jobs: Dict[str, RenderJobStatus] = {}

    def submit(self, song_id: str, render_type: RenderType) -> str:
        """
        Submit a render job.

        For the fake engine, this immediately creates a "ready" job
        with a demo audio URL.
        """
        job_id = f"job_{uuid.uuid4().hex[:16]}"

        # Create immediately ready job with fake audio URL
        job_status = RenderJobStatus(
            job_id=job_id,
            song_id=song_id,
            render_type=render_type,
            status="ready",
            audio_url=f"/demo_audio/{render_type}-{song_id}.mp3",
            error=None,
        )

        # Store job
        self._jobs[job_id] = job_status

        return job_id

    def status(self, job_id: str) -> RenderJobStatus:
        """Get the status of a render job."""
        if job_id not in self._jobs:
            # Return error status for unknown job
            return RenderJobStatus(
                job_id=job_id,
                song_id="unknown",
                render_type="full_mix",
                status="failed",
                audio_url=None,
                error=f"Job {job_id} not found",
            )

        return self._jobs[job_id]

    def get_all_jobs(self) -> list[RenderJobStatus]:
        """Get all jobs (for debugging/admin purposes)."""
        return list(self._jobs.values())


# Global singleton instance
_render_engine: RenderEngine = FakeRenderEngine()


def get_render_engine() -> RenderEngine:
    """Get the render engine (currently fake, can be swapped later)."""
    return _render_engine
