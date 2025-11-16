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
    """Test that root endpoint returns service info or frontend."""
    response = client.get("/")
    assert response.status_code == 200

    # Root can serve either JSON (dev mode) or HTML (production mode with built frontend)
    content_type = response.headers.get("content-type", "")

    if "application/json" in content_type:
        # Dev mode - JSON API response
        data = response.json()
        assert data["service"] == settings.APP_NAME
        assert data["version"] == settings.APP_VERSION
        assert data["status"] == "running"
    else:
        # Production mode - serving static frontend HTML
        assert "text/html" in content_type or content_type == ""
        # Just verify we got some content
        assert len(response.content) > 0
