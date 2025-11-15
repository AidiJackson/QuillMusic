"""
QuillMusic Backend - FastAPI Application
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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
        allow_origin_regex=r"https://.*\.(replit\.dev|repl\.co)",
        allow_origins=["http://localhost:5000", "http://localhost:5173", "http://localhost:3000", "http://localhost:8000"],
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

    # Serve static frontend files in production
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists() and frontend_dist.is_dir():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
    else:
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
