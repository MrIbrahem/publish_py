"""Tests for services.oauth_client module."""

import pytest
from unittest.mock import patch, MagicMock


class TestGetOauthClient:
    """Tests for get_oauth_client function."""

    def test_creates_oauth1_object(self):
        """Test that OAuth1 object is created correctly."""
        with patch("src.app_main.services.oauth_client.settings") as mock_settings:
            mock_settings.oauth.consumer_key = "test_consumer_key"
            mock_settings.oauth.consumer_secret = "test_consumer_secret"

            from src.app_main.services.oauth_client import get_oauth_client

            result = get_oauth_client("access_key", "access_secret", "en.wikipedia.org")

            assert result is not None
            assert result.client.client_key == "test_consumer_key"
            assert result.client.resource_owner_key == "access_key"


class TestGetCsrfToken:
    """Tests for get_csrf_token function."""

    def test_returns_token_response(self):
        """Test that CSRF token is retrieved from API."""
        with patch("src.app_main.services.oauth_client.requests") as mock_requests, \
             patch("src.app_main.services.oauth_client.settings") as mock_settings:
            mock_settings.oauth.consumer_key = "test_key"
            mock_settings.oauth.consumer_secret = "test_secret"

            mock_response = MagicMock()
            mock_response.json.return_value = {
                "query": {
                    "tokens": {
                        "csrftoken": "test_csrf_token+\\"
                    }
                }
            }
            mock_requests.get.return_value = mock_response

            from src.app_main.services.oauth_client import get_csrf_token

            result = get_csrf_token("access_key", "access_secret", "en")

            assert "query" in result
            assert "tokens" in result["query"]
            assert result["query"]["tokens"]["csrftoken"] == "test_csrf_token+\\"


class TestPostParams:
    """Tests for post_params function."""

    def test_includes_csrf_token_in_request(self):
        """Test that CSRF token is included in POST request."""
        with patch("src.app_main.services.oauth_client.get_csrf_token") as mock_get_token, \
             patch("src.app_main.services.oauth_client.requests") as mock_requests, \
             patch("src.app_main.services.oauth_client.settings") as mock_settings:
            mock_settings.oauth.consumer_key = "test_key"
            mock_settings.oauth.consumer_secret = "test_secret"

            mock_get_token.return_value = {
                "query": {"tokens": {"csrftoken": "token123"}}
            }
            mock_response = MagicMock()
            mock_response.text = '{"success": true}'
            mock_requests.post.return_value = mock_response

            from src.app_main.services.oauth_client import post_params

            result = post_params(
                {"action": "edit"},
                "https://en.wikipedia.org",
                "access_key",
                "access_secret",
            )

            assert result == '{"success": true}'
            # Verify the token was added to params
            call_args = mock_requests.post.call_args
            assert call_args[1]["data"]["token"] == "token123"

    def test_returns_error_when_csrf_fails(self):
        """Test that error is returned when CSRF token retrieval fails."""
        with patch("src.app_main.services.oauth_client.get_csrf_token") as mock_get_token, \
             patch("src.app_main.services.oauth_client.settings") as mock_settings:
            mock_settings.oauth.consumer_key = "test_key"
            mock_settings.oauth.consumer_secret = "test_secret"

            mock_get_token.return_value = {
                "error": {"code": "mwoauth-invalid-authorization"}
            }

            from src.app_main.services.oauth_client import post_params

            result = post_params(
                {"action": "edit"},
                "https://en.wikipedia.org",
                "access_key",
                "access_secret",
            )

            assert "error" in result
            assert "get_csrf_token failed" in result


class TestGetCxtoken:
    """Tests for get_cxtoken function."""

    def test_returns_cxtoken_response(self):
        """Test that cxtoken is retrieved successfully."""
        with patch("src.app_main.services.oauth_client.post_params") as mock_post:
            mock_post.return_value = '{"cxtoken": "some_cx_token"}'

            from src.app_main.services.oauth_client import get_cxtoken

            result = get_cxtoken("en", "access_key", "access_secret")

            assert "cxtoken" in result
            assert result["cxtoken"] == "some_cx_token"

    def test_returns_error_on_invalid_json(self):
        """Test that error is returned on invalid JSON response."""
        with patch("src.app_main.services.oauth_client.post_params") as mock_post:
            mock_post.return_value = "not valid json"

            from src.app_main.services.oauth_client import get_cxtoken

            result = get_cxtoken("en", "access_key", "access_secret")

            assert "error" in result
