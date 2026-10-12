"""Tests for clients.oauth_client module."""

from __future__ import annotations

import json
from typing import Any

import pytest
import requests

from src.main_app.services.clients.oauth_client import OAuthClient, get_oauth_client

_CLIENT_MODULE = "src.main_app.services.clients.oauth_client"


class FakeSettings:
    """Minimal stand-in for app_settings exposing only the oauth section."""

    class oauth:  # noqa: N801
        consumer_key = "test_consumer_key"
        consumer_secret = "test_consumer_secret"


class FakeResponse:
    """Fake HTTP response with the bits OAuthClient uses."""

    def __init__(self, json_data: Any = None, text: str = "", json_error: Exception | None = None) -> None:
        self._json_data = json_data
        self._json_error = json_error
        self.text = text

    def json(self) -> Any:
        if self._json_error is not None:
            raise self._json_error
        return self._json_data


class FakeHttpClient:
    """Fake HttpClient that returns queued responses and records every call.

    Queue items may be a FakeResponse or an Exception (which is raised).
    """

    def __init__(
        self,
        get_responses: list[FakeResponse | Exception] | None = None,
        post_responses: list[FakeResponse | Exception] | None = None,
    ) -> None:
        self.get_responses = list(get_responses or [])
        self.post_responses = list(post_responses or [])
        self.get_calls: list[dict[str, Any]] = []
        self.post_calls: list[dict[str, Any]] = []

    @staticmethod
    def _next(queue: list[FakeResponse | Exception]) -> FakeResponse:
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def _send(self, url: str, **kwargs: Any) -> FakeResponse:
        self.get_calls.append({"url": url, **kwargs})
        return self._next(self.get_responses)

    def get(self, url: str, **kwargs: Any) -> FakeResponse:
        self.get_calls.append({"url": url, **kwargs})
        return self._next(self.get_responses)

    def post(self, url: str, **kwargs: Any) -> FakeResponse:
        self.post_calls.append({"url": url, **kwargs})
        return self._next(self.post_responses)


def csrf_response(token: str = "token123") -> FakeResponse:
    return FakeResponse(json_data={"query": {"tokens": {"csrftoken": token}}})


@pytest.fixture(autouse=True)
def fake_settings(monkeypatch: pytest.MonkeyPatch) -> FakeSettings:
    """Provide OAuth consumer credentials without touching real config."""
    settings = FakeSettings()
    monkeypatch.setattr(f"{_CLIENT_MODULE}.app_settings", settings)
    return settings


class TestGetOauthClient:
    """Tests for get_oauth_client function."""

    def test_creates_oauth1_object(self):
        result = get_oauth_client("access_key", "access_secret", "en.wikipedia.org")

        assert result is not None
        assert result.client.client_key == "test_consumer_key"
        assert result.client.resource_owner_key == "access_key"


class TestGetCsrfToken:
    """Tests for OAuthClient.get_csrf_token."""

    def test_returns_token_response(self):
        token = "test_csrf_token+\\"
        http = FakeHttpClient(get_responses=[csrf_response(token)])

        client = OAuthClient(http_client=http)  # pyright: ignore[reportArgumentType]
        result = client.get_csrf_token("access_key", "access_secret", "en")

        assert result["query"]["tokens"]["csrftoken"] == token

    def test_sends_expected_request(self):
        http = FakeHttpClient(get_responses=[csrf_response()])

        client = OAuthClient(http_client=http)  # pyright: ignore[reportArgumentType]
        client.get_csrf_token("access_key", "access_secret", "fr")

        assert len(http.get_calls) == 1
        call = http.get_calls[0]
        assert call["url"] == "https://fr.wikipedia.org/w/api.php"
        assert call["params"] == {"action": "query", "meta": "tokens", "format": "json"}
        assert call["auth"].client.resource_owner_key == "access_key"

    def test_returns_error_on_connection_error(self):
        http = FakeHttpClient(get_responses=[requests.exceptions.ConnectionError("boom")])

        client = OAuthClient(http_client=http)  # pyright: ignore[reportArgumentType]
        result = client.get_csrf_token("access_key", "access_secret")

        assert result["error"]["code"] == "Connection error"
        assert result["exception"] == "boom"

    def test_returns_error_on_request_exception(self):
        http = FakeHttpClient(get_responses=[requests.exceptions.Timeout("slow")])

        client = OAuthClient(http_client=http)  # pyright: ignore[reportArgumentType]
        result = client.get_csrf_token("access_key", "access_secret")

        assert result["error"]["code"] == "Request error"
        assert result["exception"] == "slow"

    def test_returns_error_on_invalid_json(self):
        bad = FakeResponse(text="<html>", json_error=requests.exceptions.JSONDecodeError("bad", "<html>", 0))
        http = FakeHttpClient(get_responses=[bad])

        client = OAuthClient(http_client=http)  # pyright: ignore[reportArgumentType]
        result = client.get_csrf_token("access_key", "access_secret")

        assert result == {"error": "JSON decode error", "response": "<html>"}


class TestPostParams:
    """Tests for OAuthClient.post_params."""

    def test_includes_csrf_token_in_request(self):
        http = FakeHttpClient(
            get_responses=[csrf_response("token123")],
            post_responses=[FakeResponse(text='{"success": true}')],
        )

        client = OAuthClient(http_client=http)  # pyright: ignore[reportArgumentType]
        result = client.post_params(
            {"action": "edit"},
            "https://en.wikipedia.org",
            "access_key",
            "access_secret",
        )

        assert result == '{"success": true}'
        assert len(http.post_calls) == 1
        call = http.post_calls[0]
        assert call["url"] == "https://en.wikipedia.org/w/api.php"
        assert call["data"]["token"] == "token123"
        assert call["data"]["format"] == "json"
        assert call["data"]["action"] == "edit"

    def test_uses_wiki_language_from_domain_for_csrf(self):
        http = FakeHttpClient(
            get_responses=[csrf_response()],
            post_responses=[FakeResponse(text="{}")],
        )

        client = OAuthClient(http_client=http)  # pyright: ignore[reportArgumentType]
        client.post_params(
            {"action": "edit"},
            "https://ar.wikipedia.org",
            "access_key",
            "access_secret",
        )

        assert http.get_calls[0]["url"] == "https://ar.wikipedia.org/w/api.php"

    def test_returns_error_when_csrf_fails(self):
        error_response = FakeResponse(json_data={"error": {"code": "mwoauth-invalid-authorization"}})
        http = FakeHttpClient(get_responses=[error_response])

        client = OAuthClient(http_client=http)  # pyright: ignore[reportArgumentType]
        result = client.post_params(
            {"action": "edit"},
            "https://en.wikipedia.org",
            "access_key",
            "access_secret",
        )

        assert "error" in result
        assert "get_csrf_token failed" in result
        assert http.post_calls == []

    def test_returns_error_when_token_missing(self):
        http = FakeHttpClient(get_responses=[FakeResponse(json_data={"query": {"tokens": {}}})])

        client = OAuthClient(http_client=http)  # pyright: ignore[reportArgumentType]
        result = client.post_params(
            {"action": "edit"},
            "https://en.wikipedia.org",
            "access_key",
            "access_secret",
        )

        assert json.loads(result)["error"] == "get_csrf_token failed"
        assert http.post_calls == []


class TestGetCxtoken:
    """Tests for OAuthClient.get_cxtoken."""

    def test_returns_cxtoken_response(self):
        http = FakeHttpClient(
            get_responses=[csrf_response()],
            post_responses=[FakeResponse(text='{"cxtoken": "some_cx_token"}')],
        )

        client = OAuthClient(http_client=http)  # pyright: ignore[reportArgumentType]
        result = client.get_cxtoken("en", "access_key", "access_secret")

        assert result["cxtoken"] == "some_cx_token"
        assert http.post_calls[0]["data"]["action"] == "cxtoken"

    def test_returns_error_on_invalid_json(self):
        http = FakeHttpClient(
            get_responses=[csrf_response()],
            post_responses=[FakeResponse(text="not valid json")],
        )

        client = OAuthClient(http_client=http)  # pyright: ignore[reportArgumentType]
        result = client.get_cxtoken("en", "access_key", "access_secret")

        assert result["error"]["code"] == "parse-error"
