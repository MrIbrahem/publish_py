"""Tests for clients.oauth_client module."""

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest


@dataclass
class MockOAuthClientDeps:
    app_settings: MagicMock
    requests: MagicMock


def mock_attr(monkeypatch, attr_name, mock):
    _client = "src.main_app.services.clients.oauth_client"
    monkeypatch.setattr(f"{_client}.{attr_name}", mock)
    monkeypatch.setattr(f"{_client}.OAuthClient.{attr_name}", mock)


@pytest.fixture
def mock_oauth_deps(monkeypatch: pytest.MonkeyPatch) -> MockOAuthClientDeps:
    """Fixture to bundle and set up common patches for oauth client tests."""
    _client = "src.main_app.services.clients.oauth_client"

    mock_settings = MagicMock()
    mock_settings.oauth.consumer_key = "test_consumer_key"
    mock_settings.oauth.consumer_secret = "test_consumer_secret"

    mock_requests = MagicMock()

    monkeypatch.setattr(f"{_client}.app_settings", mock_settings)
    monkeypatch.setattr(f"{_client}.requests", mock_requests)

    return MockOAuthClientDeps(
        app_settings=mock_settings,
        requests=mock_requests,
    )


class TestGetOauthClient:
    """Tests for get_oauth_client function and OAuthClient."""

    def test_creates_oauth1_object(self, mock_oauth_deps: MockOAuthClientDeps):
        """Test that OAuth1 object is created correctly."""
        from src.main_app.services.clients.oauth_client import OAuthClient

        result = OAuthClient.get_oauth_client("access_key", "access_secret", "en.wikipedia.org")

        assert result is not None
        assert result.client.client_key == "test_consumer_key"
        assert result.client.resource_owner_key == "access_key"


class TestGetCsrfToken:
    """Tests for get_csrf_token function and OAuthClient."""

    def test_returns_token_response(self, mock_oauth_deps: MockOAuthClientDeps):
        """Test that CSRF token is retrieved from API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"query": {"tokens": {"csrftoken": "test_csrf_token+\\"}}}
        mock_oauth_deps.requests.get.return_value = mock_response

        from src.main_app.services.clients.oauth_client import OAuthClient

        result = OAuthClient.get_csrf_token("access_key", "access_secret", "en")

        assert "query" in result
        assert "tokens" in result["query"]
        assert result["query"]["tokens"]["csrftoken"] == "test_csrf_token+\\"


class TestPostParams:
    """Tests for post_params function and OAuthClient."""

    def test_includes_csrf_token_in_request(
        self, monkeypatch: pytest.MonkeyPatch, mock_oauth_deps: MockOAuthClientDeps
    ):
        """Test that CSRF token is included in POST request."""
        mock_get_token = MagicMock(return_value={"query": {"tokens": {"csrftoken": "token123"}}})
        mock_attr(monkeypatch, "get_csrf_token", mock_get_token)

        mock_response = MagicMock()
        mock_response.text = '{"success": true}'
        mock_oauth_deps.requests.post.return_value = mock_response

        from src.main_app.services.clients.oauth_client import OAuthClient

        result = OAuthClient.post_params(
            {"action": "edit"},
            "https://en.wikipedia.org",
            "access_key",
            "access_secret",
        )

        assert result == '{"success": true}'
        # Verify the token was added to params
        call_args = mock_oauth_deps.requests.post.call_args
        assert call_args[1]["data"]["token"] == "token123"

    def test_returns_error_when_csrf_fails(self, monkeypatch: pytest.MonkeyPatch, mock_oauth_deps: MockOAuthClientDeps):
        """Test that error is returned when CSRF token retrieval fails."""
        mock_get_token = MagicMock(return_value={"error": {"code": "mwoauth-invalid-authorization"}})
        mock_attr(monkeypatch, "get_csrf_token", mock_get_token)

        from src.main_app.services.clients.oauth_client import OAuthClient

        result = OAuthClient.post_params(
            {"action": "edit"},
            "https://en.wikipedia.org",
            "access_key",
            "access_secret",
        )

        assert "error" in result
        assert "get_csrf_token failed" in result


class TestGetCxtoken:
    """Tests for get_cxtoken function and OAuthClient."""

    def test_returns_cxtoken_response(self, monkeypatch: pytest.MonkeyPatch):
        """Test that cxtoken is retrieved successfully."""
        mock_post = MagicMock(return_value='{"cxtoken": "some_cx_token"}')
        mock_attr(monkeypatch, "post_params", mock_post)

        from src.main_app.services.clients.oauth_client import OAuthClient

        result = OAuthClient.get_cxtoken("en", "access_key", "access_secret")

        assert "cxtoken" in result
        assert result["cxtoken"] == "some_cx_token"

    def test_returns_error_on_invalid_json(self, monkeypatch: pytest.MonkeyPatch):
        """Test that error is returned on invalid JSON response."""
        mock_post = MagicMock(return_value="not valid json")
        mock_attr(monkeypatch, "post_params", mock_post)

        from src.main_app.services.clients.oauth_client import OAuthClient

        result = OAuthClient.get_cxtoken("en", "access_key", "access_secret")

        assert "error" in result
