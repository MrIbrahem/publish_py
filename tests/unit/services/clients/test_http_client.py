"""Unit tests for HttpClient in src/main_app/services/clients/http_client.py."""

from unittest.mock import MagicMock, patch

from src.main_app.services.clients.http_client import HttpClient


class TestHttpClient:
    """Test suite for HttpClient class."""

    def test_default_user_agent_setting(self):
        client = HttpClient(user_agent="CustomAgent/1.0")
        headers = client._prepare_headers(None)
        assert headers["User-Agent"] == "CustomAgent/1.0"

    def test_custom_headers_preserve_user_agent(self):
        client = HttpClient(user_agent="CustomAgent/1.0")
        headers = client._prepare_headers({"Authorization": "Bearer token"})
        assert headers["Authorization"] == "Bearer token"
        assert headers["User-Agent"] == "CustomAgent/1.0"

    def test_custom_user_agent_in_headers_not_overwritten(self):
        client = HttpClient(user_agent="CustomAgent/1.0")
        headers = client._prepare_headers({"User-Agent": "Override/2.0"})
        assert headers["User-Agent"] == "Override/2.0"

    @patch("requests.request")
    def test_get_request(self, mock_get):
        mock_response = MagicMock()
        mock_get.return_value = mock_response

        client = HttpClient(default_timeout=15.0, user_agent="TestAgent/1.0")
        resp = client.get("https://example.com/api", params={"q": "test"})

        assert resp == mock_response
        mock_get.assert_called_once_with(
            method="GET",
            url="https://example.com/api",
            headers={"User-Agent": "TestAgent/1.0"},
            timeout=15.0,
            params={"q": "test"},
            auth=None,
        )

    @patch("requests.request")
    def test_post_request(self, mock_post):
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        client = HttpClient(default_timeout=20.0, user_agent="TestAgent/1.0")
        resp = client.post("https://example.com/api", data={"key": "val"})

        assert resp == mock_response
        mock_post.assert_called_once_with(
            method="POST",
            url="https://example.com/api",
            headers={"User-Agent": "TestAgent/1.0"},
            timeout=20.0,
            data={"key": "val"},
            json=None,
            params=None,
            auth=None,
        )
