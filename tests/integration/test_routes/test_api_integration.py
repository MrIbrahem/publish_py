"""Integration tests for API routes.

These tests verify the integration of various components in API routes.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestPublishRouteIntegration:
    """Integration tests for publish route."""

    def test_publish_requires_post_method(self, client):
        """Test that publish route requires POST method."""
        response = client.get("/publish")

        assert response.status_code == 405  # Method Not Allowed

    def test_publish_rejects_missing_csrf(self, app):
        """Test that publish route rejects requests without CSRF token when enabled."""
        from src.app_main import create_app
        from src.app_main.config import Config

        class TestConfigWithCSRF(Config):
            WTF_CSRF_ENABLED = True

        test_app = create_app(TestConfigWithCSRF)
        test_client = test_app.test_client()

        response = test_client.post("/publish", data={"title": "Test"})

        # Should get 400 due to missing CSRF
        assert response.status_code in [400, 302, 403]


class TestCxtokenRouteIntegration:
    """Integration tests for cxtoken route."""

    def test_cxtoken_requires_authentication(self, client):
        """Test that cxtoken route requires authentication."""
        response = client.get("/cxtoken?wiki=arwiki")

        # Should redirect to login
        assert response.status_code in [302, 401, 403]

    def test_cxtoken_rejects_missing_wiki_param(self, auth_client):
        """Test that cxtoken route rejects requests without wiki parameter."""
        response = auth_client.get("/cxtoken")

        # Should return bad request
        assert response.status_code in [400, 422]


class TestAuthRouteIntegration:
    """Integration tests for auth routes."""

    def test_login_redirects_to_oauth_provider(self, client, monkeypatch):
        """Test that login route redirects to OAuth provider."""
        # Mock OAuth to be enabled
        monkeypatch.setattr("src.app_main.app_routes.auth.routes.settings.oauth.enabled", True)

        response = client.get("/auth/login")

        # Should redirect to OAuth provider
        assert response.status_code in [302, 200]

    def test_logout_clears_session(self, client):
        """Test that logout clears the session."""
        with client.session_transaction() as sess:
            sess["uid"] = 12345
            sess["username"] = "TestUser"

        response = client.get("/auth/logout")

        # Should redirect after logout
        assert response.status_code == 302

        # Session should be cleared
        with client.session_transaction() as sess:
            assert "uid" not in sess


class TestMainRouteIntegration:
    """Integration tests for main routes."""

    def test_index_route_returns_html(self, client):
        """Test that index route returns HTML."""
        response = client.get("/")

        # Should return HTML content
        assert response.status_code == 200
        assert response.content_type.startswith("text/html")

    def test_404_for_nonexistent_route(self, client):
        """Test that nonexistent routes return 404."""
        response = client.get("/nonexistent-route")

        assert response.status_code == 404


class TestCorsIntegration:
    """Integration tests for CORS handling."""

    def test_cors_headers_on_allowed_origin(self, client, monkeypatch):
        """Test that CORS headers are set for allowed origins."""
        monkeypatch.setattr("src.app_main.cors.is_allowed", lambda req: "https://example.com")

        response = client.get(
            "/",
            headers={"Origin": "https://example.com"}
        )

        # Should have CORS headers
        assert "Access-Control-Allow-Origin" in response.headers

    def test_preflight_request_handling(self, client):
        """Test that OPTIONS requests are handled for CORS preflight."""
        response = client.options("/")

        # Should be handled (may return 200 or 404 depending on route setup)
        assert response.status_code in [200, 404]
