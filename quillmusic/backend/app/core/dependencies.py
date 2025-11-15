"""
QuillMusic Backend Dependencies
"""
from typing import Generator, Optional
import redis
from redis import Redis
from rq import Queue

from app.core.config import settings


# Redis connection pool (singleton pattern)
_redis_client: Optional[Redis] = None


def get_redis() -> Redis:
    """Get Redis connection."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _redis_client


def get_render_queue() -> Queue:
    """Get RQ queue for render jobs."""
    redis_conn = get_redis()
    return Queue("renders", connection=redis_conn)


def get_blueprint_queue() -> Queue:
    """Get RQ queue for blueprint generation jobs."""
    redis_conn = get_redis()
    return Queue("blueprints", connection=redis_conn)
