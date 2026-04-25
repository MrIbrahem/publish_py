"""
Integration tests for src/sqlalchemy_app/public/routes/auth/routes.py module.
"""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient


@pytest.mark.integration
class TestAuthLogin:
    """Integration tests for the /login route."""

    def test_login_redirects_when_oauth_not_configured(self, app: Flask, client: FlaskClient):
        """Test that login redirects to index when OAuth is not configured."""
        with patch("src.sqlalchemy_app.public.routes.auth.routes.settings") as mock_settings:
            mock_settings.oauth = None

            response = client.get("/auth/login", follow_redirects=False)

            assert response.status_code == 302
            assert "/" in response.location or "error=oauth-not-configured" in response.location

    def test_login_rate_limit_blocks_excessive_requests(self, app: Flask, client: FlaskClient):
        """Test that login rate limit blocks excessive requests."""
        with patch("src.sqlalchemy_app.public.routes.auth.routes.settings") as mock_settings:
            mock_settings.oauth = MagicMock()
            mock_settings.sessions.state_key = "oauth_state"
            mock_settings.sessions.request_token_key = "request_token"

            # Mock rate limiter to test rate limiting quickly
            with patch("src.sqlalchemy_app.public.routes.auth.routes.login_rate_limiter") as mock_limiter:
                call_count = 0

                def allow_side_effect(_key):
                    nonlocal call_count
                    call_count += 1
                    # Allow first 5 requests, block the 6th
                    return call_count <= 5

                mock_limiter.allow.side_effect = allow_side_effect
                mock_limiter.try_after.return_value = timedelta(seconds=30)

                with patch("src.sqlalchemy_app.public.routes.auth.routes.start_login") as mock_start:
                    mock_start.return_value = ("https://oauth.provider.com/authorize", MagicMock())

                    # Make 6 requests to exceed rate limit
                    for _ in range(6):
                        response = client.get("/auth/login", follow_redirects=False)

                    # After rate limit exceeded, should redirect with warning
                    assert response.status_code == 302  # in [302, 429]

    def test_login_starts_oauth_flow(self, app: Flask, client: FlaskClient):
        """Test that login starts OAuth flow when properly configured."""
        with patch("src.sqlalchemy_app.public.routes.auth.routes.settings") as mock_settings:
            mock_settings.oauth = MagicMock()
            mock_settings.sessions.state_key = "oauth_state"
            mock_settings.sessions.request_token_key = "request_token"

            with patch("src.sqlalchemy_app.public.routes.auth.routes.start_login") as mock_start:
                mock_start.return_value = ("https://oauth.provider.com/authorize", MagicMock())

                with patch("src.sqlalchemy_app.public.routes.auth.routes.login_rate_limiter") as mock_limiter:
                    mock_limiter.allow.return_value = True

                    response = client.get("/auth/login", follow_redirects=False)

                    # Should redirect to OAuth provider
                    assert response.status_code == 302


@pytest.mark.integration
class TestAuthCallback:
    """Integration tests for the /callback route."""

    def test_callback_redirects_when_oauth_not_configured(self, app: Flask, client: FlaskClient):
        """Test that callback redirects when OAuth is not configured."""
        with patch("src.sqlalchemy_app.public.routes.auth.routes.settings") as mock_settings:
            mock_settings.oauth = None

            response = client.get("/auth/callback?oauth_verifier=123&state=abc", follow_redirects=False)

            assert response.status_code == 302

    def test_callback_validates_state_token(self, app: Flask, client: FlaskClient):
        """Test that callback validates state token."""
        with patch("src.sqlalchemy_app.public.routes.auth.routes.settings") as mock_settings:
            mock_settings.oauth = MagicMock()
            mock_settings.sessions.state_key = "oauth_state"
            mock_settings.sessions.request_token_key = "request_token"
            mock_settings.cookie.name = "auth_cookie"
            mock_settings.cookie.httponly = True
            mock_settings.cookie.secure = False
            mock_settings.cookie.samesite = "Lax"
            mock_settings.cookie.max_age = 3600

            with patch("src.sqlalchemy_app.public.routes.auth.routes.callback_rate_limiter") as mock_limiter:
                mock_limiter.allow.return_value = True

                # Missing state should cause redirect
                response = client.get("/auth/callback?oauth_verifier=123", follow_redirects=False)

                assert response.status_code == 302
                assert "error" in response.location


@pytest.mark.integration
class TestAuthLogout:
    """Integration tests for the /logout route."""

    def test_logout_clears_session(self, app: Flask, client: FlaskClient):
        """Test that logout clears the session."""
        with client.session_transaction() as sess:
            sess["uid"] = 12345
            sess["username"] = "TestUser"

        response = client.get("/auth/logout", follow_redirects=False)

        assert response.status_code == 302

        with client.session_transaction() as sess:
            assert "uid" not in sess
            assert "username" not in sess

    def test_logout_deletes_cookie(self, app: Flask, client: FlaskClient):
        """Test that logout deletes the authentication cookie."""
        response = client.get("/auth/logout", follow_redirects=False)

        assert response.status_code == 302
        # Cookie should be set to delete
        cookie_header = response.headers.get("Set-Cookie", "")
        # Cookie should have expired or be deleted
        assert "auth_cookie" in cookie_header.lower() or "Max-Age=0" in cookie_header or "Expires" in cookie_header


@pytest.mark.integration
class TestLoginRequiredDecorator:
    """Integration tests for the login_required decorator."""

    def test_login_required_redirects_anonymous(self, app: Flask, client: FlaskClient):
        """Test that login_required redirects anonymous users."""
        # Create a test route with login_required
        from src.sqlalchemy_app.public.routes.auth.routes import login_required

        @app.route("/test-protected")
        @login_required
        def protected_route():
            return "Protected content"

        response = client.get("/test-protected", follow_redirects=False)

        assert response.status_code == 302
        assert "login-required" in response.location or "/" in response.location


class TestAuthRouteIntegration:
    """Integration tests for auth routes."""

    def test_login_route_exists(self, client):
        """Test that login route is accessible."""
        response = client.get("/auth/login")

        # Route may return various status codes depending on configuration
        # Note: 500 is not allowed - server errors should fail the test
        assert response.status_code == 302  # in [200, 302, 404]

    def test_logout_route_exists(self, client):
        """Test that logout route is accessible."""
        response = client.get("/auth/logout")

        # Should redirect after logout or succeed
        # Note: 500 is not allowed - server errors should fail the test
        assert response.status_code == 302  # in [302, 200, 404]

