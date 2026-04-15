"""Unit tests for users.current module.

Tests for current user helpers and authentication decorators.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.app_main.users.current import (
    CurrentUser,
    _resolve_user_id,
    current_user,
    oauth_required,
)


class TestCurrentUser:
    """Tests for CurrentUser dataclass."""

    def test_create_with_fields(self):
        """Test creating CurrentUser with fields."""
        user = CurrentUser(user_id="12345", username="TestUser")

        assert user.user_id == "12345"
        assert user.username == "TestUser"

    def test_is_frozen(self):
        """Test that CurrentUser is immutable."""
        user = CurrentUser(user_id="12345", username="TestUser")

        with pytest.raises(AttributeError):
            user.user_id = "99999"


class TestResolveUserId:
    """Tests for _resolve_user_id function."""

    def test_returns_int_from_session(self, app):
        """Test that int uid from session is returned."""
        with app.test_request_context():
            from flask import session

            session["uid"] = 12345

            result = _resolve_user_id()

            assert result == 12345
            assert isinstance(result, int)

    def test_converts_string_uid_to_int(self, app):
        """Test that string uid is converted to int."""
        with app.test_request_context():
            from flask import session

            session["uid"] = "12345"

            result = _resolve_user_id()

            assert result == 12345
            assert isinstance(result, int)

    def test_returns_none_when_no_uid(self, app):
        """Test that None is returned when no uid in session."""
        with app.test_request_context():
            result = _resolve_user_id()

            assert result is None

    def test_returns_none_for_invalid_uid(self, app):
        """Test that None is returned for invalid uid."""
        with app.test_request_context():
            from flask import session

            session["uid"] = "not_a_number"

            result = _resolve_user_id()

            assert result is None


class TestCurrentUserFunction:
    """Tests for current_user function."""

    def test_returns_none_when_no_user_id(self, app):
        """Test that None is returned when no user ID found."""
        with app.test_request_context():
            result = current_user()

            assert result is None

    def test_returns_user_from_session(self, app, monkeypatch):
        """Test that user is returned from session."""
        mock_user = MagicMock()
        mock_user.username = "TestUser"

        def mock_get_user_token(uid):
            if uid == 12345:
                return mock_user
            return None

        monkeypatch.setattr("src.app_main.users.current.get_user_token", mock_get_user_token)

        with app.test_request_context():
            from flask import session

            session["uid"] = 12345

            result = current_user()

            assert result is mock_user

    def test_updates_session_username(self, app, monkeypatch):
        """Test that session username is updated from user record."""
        mock_user = MagicMock()
        mock_user.username = "UpdatedName"

        monkeypatch.setattr("src.app_main.users.current.get_user_token", lambda uid: mock_user)

        with app.test_request_context():
            from flask import session

            session["uid"] = 12345
            session["username"] = "OldName"

            current_user()

            assert session["username"] == "UpdatedName"


class TestOAuthRequired:
    """Tests for oauth_required decorator."""

    def test_redirects_when_no_user_and_oauth_enabled(self, app, monkeypatch):
        """Test that decorator redirects when no user and OAuth enabled."""
        from src.app_main.config import OAuthConfig, Settings

        monkeypatch.setattr("src.app_main.users.current.current_user", lambda: None)
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
        monkeypatch.setattr("src.app_main.users.current.settings", mock_settings)

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
        monkeypatch.setattr("src.app_main.users.current.current_user", lambda: mock_user)
        # Create a mock Settings object with OAuth enabled
        mock_settings = MagicMock()
        mock_settings.oauth = OAuthConfig(
            mw_uri="https://test.com",
            consumer_key="test_key",
            consumer_secret="test_secret",
            encryption_key="test_encryption_key",
            enabled=True,
        )
        monkeypatch.setattr("src.app_main.users.current.settings", mock_settings)

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
        monkeypatch.setattr("src.app_main.users.current.settings", mock_settings)

        @oauth_required
        def protected_view():
            return "success"

        with app.test_request_context():
            result = protected_view()

            assert result == "success"

    def test_allows_access_when_oauth_disabled(self, app, monkeypatch):
        """Test that decorator allows access when OAuth is disabled."""
        from src.app_main.config import OAuthConfig

        # Create a mock OAuth config with enabled=False
        mock_oauth = OAuthConfig(
            mw_uri="https://test.com",
            consumer_key="test_key",
            consumer_secret="test_secret",
            encryption_key="test_encryption_key",
            enabled=False,
        )
        monkeypatch.setattr("src.app_main.users.current.settings.oauth", mock_oauth)

        @oauth_required
        def protected_view():
            return "success"

        with app.test_request_context():
            result = protected_view()

            assert result == "success"
