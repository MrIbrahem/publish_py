"""
Unit tests for auth.decorators module.

Tests for authentication decorators.
"""

from unittest.mock import MagicMock

from src.new_app.shared.auth.decorators import (
    oauth_required,
)


class TestOAuthRequired:
    """Tests for oauth_required decorator."""

    def test_redirects_when_no_user_and_oauth_enabled(self, app, monkeypatch):
        """Test that decorator redirects when no user and OAuth enabled."""
        from src.app_main.config import OAuthConfig, Settings

        monkeypatch.setattr("src.new_app.shared.auth.decorators.current_user", lambda: None)
        # Create a mock Settings object with OAuth enabled
        mock_settings = MagicMock()
        mock_settings.oauth = OAuthConfig(
            mw_uri="https://test.com",
            consumer_key="test_key",
            consumer_secret="test_secret",
            encryption_key="test_encryption_key",
            enabled=True,
        )
        # Patch the entire settings object, not just oauth
        monkeypatch.setattr("src.new_app.shared.auth.decorators.settings", mock_settings)

        @oauth_required
        def protected_view():
            return "success"

        with app.test_request_context():
            from flask import session

            session["uid"] = None

            result = protected_view()

            assert result.status_code == 302  # Redirect

    def test_allows_access_when_user_present(self, app, monkeypatch):
        """Test that decorator allows access when user is present."""
        from src.app_main.config import OAuthConfig

        mock_user = MagicMock()
        monkeypatch.setattr("src.new_app.shared.auth.decorators.current_user", lambda: mock_user)
        # Create a mock Settings object with OAuth enabled
        mock_settings = MagicMock()
        mock_settings.oauth = OAuthConfig(
            mw_uri="https://test.com",
            consumer_key="test_key",
            consumer_secret="test_secret",
            encryption_key="test_encryption_key",
            enabled=True,
        )
        monkeypatch.setattr("src.new_app.shared.auth.decorators.settings", mock_settings)

        @oauth_required
        def protected_view():
            return "success"

        with app.test_request_context():
            result = protected_view()

            assert result == "success"

    def test_allows_access_when_oauth_disabled(self, app, monkeypatch):
        """Test that decorator allows access when OAuth is disabled."""
        from src.app_main.config import OAuthConfig

        # Create a mock Settings object with OAuth disabled
        mock_settings = MagicMock()
        mock_settings.oauth = OAuthConfig(
            mw_uri="https://test.com",
            consumer_key="test_key",
            consumer_secret="test_secret",
            encryption_key="test_encryption_key",
            enabled=False,
        )
        monkeypatch.setattr("src.new_app.shared.auth.decorators.settings", mock_settings)

        @oauth_required
        def protected_view():
            return "success"

        with app.test_request_context():
            result = protected_view()

            assert result == "success"

    def test_allows_access_when_oauth_null(self, app, monkeypatch):
        """Test that decorator allows access when OAuth is None (disabled)."""
        from src.app_main.config import OAuthConfig

        # Create a mock Settings object with oauth=None
        mock_settings = MagicMock()
        mock_settings.oauth = None
        monkeypatch.setattr("src.new_app.shared.auth.decorators.settings", mock_settings)

        @oauth_required
        def protected_view():
            return "success"

        with app.test_request_context():
            result = protected_view()

            assert result == "success"
