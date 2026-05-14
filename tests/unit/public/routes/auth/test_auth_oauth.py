"""
Unit tests for src/sqlalchemy_app/public/routes/auth/oauth.py module.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.sqlalchemy_app.public.routes.auth.oauth import (
    IDENTITY_ERROR_MESSAGE,
    OAuthIdentityError,
    complete_login,
    get_handshaker,
    start_login,
)


class TestOAuthIdentityError:
    """Tests for OAuthIdentityError exception."""

    def test_exception_with_message(self):
        """Test that exception stores the message."""
        error = OAuthIdentityError("Test error message")
        assert str(error) == "Test error message"

    def test_exception_with_original_exception(self):
        """Test that exception stores original exception."""
        original = ValueError("Original error")
        error = OAuthIdentityError("Test error", original_exception=original)
        assert error.original_exception is original

    def test_exception_without_original_exception(self):
        """Test that exception can be created without original exception."""
        error = OAuthIdentityError("Test error")
        assert error.original_exception is None

    def test_exception_inheritance(self):
        """Test that OAuthIdentityError inherits from Exception."""
        assert issubclass(OAuthIdentityError, Exception)


class TestGetHandshaker:
    """Tests for get_handshaker function."""

    def test_raises_when_oauth_config_none(self):
        """Test that RuntimeError is raised when OAuth config is None."""
        with patch("src.sqlalchemy_app.public.routes.auth.oauth.settings") as mock_settings:
            mock_settings.oauth = None

            with pytest.raises(RuntimeError, match="MediaWiki OAuth configuration is incomplete"):
                get_handshaker()

    @patch("src.sqlalchemy_app.public.routes.auth.oauth.mwoauth")
    def test_creates_handshaker_with_correct_params(self, mock_mwoauth):
        """Test that handshaker is created with correct parameters."""
        mock_consumer_token = MagicMock()
        mock_mwoauth.ConsumerToken.return_value = mock_consumer_token
        mock_handshaker_instance = MagicMock()
        mock_mwoauth.Handshaker.return_value = mock_handshaker_instance

        with patch("src.sqlalchemy_app.public.routes.auth.oauth.settings") as mock_settings:
            mock_settings.oauth.consumer_key = "test_key"
            mock_settings.oauth.consumer_secret = "test_secret"
            mock_settings.oauth.mw_uri = "https://test.wiki/w/index.php"
            mock_settings.user_agent = "TestAgent/1.0"

            result = get_handshaker()

            mock_mwoauth.ConsumerToken.assert_called_once_with("test_key", "test_secret")
            mock_mwoauth.Handshaker.assert_called_once_with(
                "https://test.wiki/w/index.php",
                consumer_token=mock_consumer_token,
                user_agent="TestAgent/1.0",
            )
            assert result is mock_handshaker_instance


class TestStartLogin:
    """Tests for start_login function."""

    @patch("src.sqlalchemy_app.public.routes.auth.oauth.get_handshaker")
    @patch("src.sqlalchemy_app.public.routes.auth.oauth.url_for")
    def test_returns_redirect_url_and_request_token(self, mock_url_for, mock_get_handshaker):
        """Test that function returns redirect URL and request token."""
        mock_url_for.return_value = "https://example.com/callback"
        mock_handshaker = MagicMock()
        mock_handshaker.initiate.return_value = ("https://oauth.provider.com/authorize", "request_token_123")
        mock_get_handshaker.return_value = mock_handshaker

        redirect_url, request_token = start_login("state_token_123")

        mock_url_for.assert_called_once_with("auth.callback", _external=True, state="state_token_123")
        mock_handshaker.initiate.assert_called_once_with(callback="https://example.com/callback")
        assert redirect_url == "https://oauth.provider.com/authorize"
        assert request_token == "request_token_123"

    @patch("src.sqlalchemy_app.public.routes.auth.oauth.get_handshaker")
    @patch("src.sqlalchemy_app.public.routes.auth.oauth.url_for")
    def test_uses_provided_state_token(self, mock_url_for, mock_get_handshaker):
        """Test that the provided state token is used in the callback URL."""
        mock_url_for.return_value = "https://example.com/callback?state=abc123"
        mock_handshaker = MagicMock()
        mock_handshaker.initiate.return_value = ("https://oauth.provider.com/authorize", "token")
        mock_get_handshaker.return_value = mock_handshaker

        start_login("abc123")

        mock_url_for.assert_called_once_with("auth.callback", _external=True, state="abc123")


class TestCompleteLogin:
    """Tests for complete_login function."""

    @patch("src.sqlalchemy_app.public.routes.auth.oauth.get_handshaker")
    def test_returns_access_token_and_identity(self, mock_get_handshaker):
        """Test that function returns access token and user identity."""
        mock_handshaker = MagicMock()
        mock_access_token = MagicMock()
        mock_identity = {"username": "TestUser", "id": 12345}
        mock_handshaker.complete.return_value = mock_access_token
        mock_handshaker.identify.return_value = mock_identity
        mock_get_handshaker.return_value = mock_handshaker

        request_token = "request_token_123"
        query_string = "oauth_verifier=abc123"

        access_token, identity = complete_login(request_token, query_string)

        mock_handshaker.complete.assert_called_once_with(request_token, query_string)
        mock_handshaker.identify.assert_called_once_with(mock_access_token)
        assert access_token is mock_access_token
        assert identity is mock_identity

    @patch("src.sqlalchemy_app.public.routes.auth.oauth.get_handshaker")
    def test_raises_identity_error_when_identify_fails(self, mock_get_handshaker):
        """Test that OAuthIdentityError is raised when identity verification fails."""
        mock_handshaker = MagicMock()
        mock_handshaker.complete.return_value = MagicMock()
        mock_handshaker.identify.side_effect = Exception("Identity verification failed")
        mock_get_handshaker.return_value = mock_handshaker

        request_token = "request_token_123"
        query_string = "oauth_verifier=abc123"

        with pytest.raises(OAuthIdentityError) as exc_info:
            complete_login(request_token, query_string)

        assert str(exc_info.value) == IDENTITY_ERROR_MESSAGE
        assert exc_info.value.original_exception is not None

    @patch("src.sqlalchemy_app.public.routes.auth.oauth.get_handshaker")
    def test_identity_error_message_constant(self, mock_get_handshaker):
        """Test that the correct error message constant is used."""
        mock_handshaker = MagicMock()
        mock_handshaker.complete.return_value = MagicMock()
        mock_handshaker.identify.side_effect = Exception("Any error")
        mock_get_handshaker.return_value = mock_handshaker

        with pytest.raises(OAuthIdentityError, match=IDENTITY_ERROR_MESSAGE):
            complete_login("token", "query")

    @patch("src.sqlalchemy_app.public.routes.auth.oauth.get_handshaker")
    def test_handles_identity_with_username(self, mock_get_handshaker):
        """Test handling identity response with username field."""
        mock_handshaker = MagicMock()
        mock_handshaker.complete.return_value = MagicMock()
        mock_handshaker.identify.return_value = {"username": "TestUser"}
        mock_get_handshaker.return_value = mock_handshaker

        _, identity = complete_login("token", "query")

        assert identity["username"] == "TestUser"

    @patch("src.sqlalchemy_app.public.routes.auth.oauth.get_handshaker")
    def test_handles_identity_with_name_field(self, mock_get_handshaker):
        """Test handling identity response with name field (fallback)."""
        mock_handshaker = MagicMock()
        mock_handshaker.complete.return_value = MagicMock()
        mock_handshaker.identify.return_value = {"name": "TestUser"}
        mock_get_handshaker.return_value = mock_handshaker

        _, identity = complete_login("token", "query")

        assert identity["name"] == "TestUser"


class TestIdentityErrorMessage:
    """Tests for the IDENTITY_ERROR_MESSAGE constant."""

    def test_message_is_string(self):
        """Test that error message is a string."""
        assert isinstance(IDENTITY_ERROR_MESSAGE, str)

    def test_message_is_not_empty(self):
        """Test that error message is not empty."""
        assert len(IDENTITY_ERROR_MESSAGE) > 0

    def test_message_contains_relevant_keywords(self):
        """Test that error message contains relevant keywords."""
        assert "verify" in IDENTITY_ERROR_MESSAGE.lower() or "identity" in IDENTITY_ERROR_MESSAGE.lower()


class TestOAuthIntegration:
    """Integration-style tests for OAuth flow."""

    @patch("src.sqlalchemy_app.public.routes.auth.oauth.get_handshaker")
    @patch("src.sqlalchemy_app.public.routes.auth.oauth.url_for")
    def test_full_oauth_flow(self, mock_url_for, mock_get_handshaker):
        """Test complete OAuth flow from start to completion."""
        # Setup mocks
        mock_url_for.return_value = "https://example.com/callback"
        mock_handshaker = MagicMock()
        mock_request_token = "request_token_abc"
        mock_access_token = MagicMock()
        mock_identity = {"username": "TestUser", "id": 12345, "groups": ["user"]}

        mock_handshaker.initiate.return_value = ("https://oauth.provider.com/authorize", mock_request_token)
        mock_handshaker.complete.return_value = mock_access_token
        mock_handshaker.identify.return_value = mock_identity
        mock_get_handshaker.return_value = mock_handshaker

        # Step 1: Start login
        redirect_url, request_token = start_login("state_123")
        assert redirect_url == "https://oauth.provider.com/authorize"
        assert request_token == mock_request_token

        # Step 2: Complete login (user returns from OAuth provider)
        query_string = "oauth_verifier=verifier123&oauth_token=token123"
        access_token, identity = complete_login(request_token, query_string)

        assert access_token is mock_access_token
        assert identity is mock_identity
        assert identity["username"] == "TestUser"
