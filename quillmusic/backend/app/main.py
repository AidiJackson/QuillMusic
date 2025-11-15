"""
QuillMusic Backend - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import health, song_blueprints, renders, manual


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize database
    init_db()

    # Include routers
    app.include_router(health.router, prefix=settings.API_PREFIX, tags=["health"])
    app.include_router(
        song_blueprints.router, prefix=settings.API_PREFIX, tags=["songs"]
    )
    app.include_router(renders.router, prefix=settings.API_PREFIX, tags=["renders"])
    app.include_router(manual.router, prefix=settings.API_PREFIX, tags=["manual"])

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
        }

    return app


app = create_app()
