"""
Tests for health check endpoint
"""
from app.core.config import settings


def test_health_check(client):
    """Test that health check returns correct status."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION


def test_root_endpoint(client):
    """Test that root endpoint returns service info."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["service"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
    assert data["status"] == "running"
