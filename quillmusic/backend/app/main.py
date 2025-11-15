"""
QuillMusic Backend - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import health, song_blueprints, renders


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
        allow_origin_regex=r"https://.*\.(replit\.dev|repl\.co)",
        allow_origins=["http://localhost:5000", "http://localhost:5173", "http://localhost:3000", "http://localhost:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix=settings.API_PREFIX, tags=["health"])
    app.include_router(
        song_blueprints.router, prefix=settings.API_PREFIX, tags=["songs"]
    )
    app.include_router(renders.router, prefix=settings.API_PREFIX, tags=["renders"])

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
