"""
Tests for cors wrappers module, to test response.headers["Access-Control-Allow-Origin"] value
"""

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from src.main_app.services.core.cors import check_cors


def _make_response_with_headers() -> MagicMock:
    """Create a mock response with a real dict headers attribute."""
    response = MagicMock()
    response.headers = {}
    return response


@dataclass
class MockCorsDeps:
    load_request: MagicMock
    get_allowed_domains: MagicMock


@pytest.fixture
def mock_cors_deps(mocker) -> MockCorsDeps:
    """Fixture to bundle common CORS request and allowed domains mocks."""
    mock_load_request = mocker.patch("src.main_app.services.core.cors._load_request")
    mock_get_allowed_domains = mocker.patch("src.main_app.services.core.cors.is_allowed_checker._get_allowed_domains")
    return MockCorsDeps(
        load_request=mock_load_request,
        get_allowed_domains=mock_get_allowed_domains,
    )


class TestCheckCorsDecoratedWithCorsDisabled:
    def test_basics_empty_headers(self, mock_app, mock_cors_deps: MockCorsDeps):
        response = MagicMock(
            headers={
                "Referer": "",
                "Origin": "",
            },
            host_url="",
        )
        mock_app.config["CORS_DISABLED"] = True
        mock_cors_deps.load_request.return_value = response

        decorated = check_cors(lambda: _make_response_with_headers())
        result = decorated()

        assert result.headers["Access-Control-Allow-Origin"] == "*"

    def test_with_headers(self, mock_app, mock_cors_deps: MockCorsDeps):
        response = MagicMock(
            headers={
                "Referer": "https://google.com",
                "Origin": "http://google.com",
            },
            host_url="https://books.google.com",
        )
        mock_app.config["CORS_DISABLED"] = True
        mock_cors_deps.load_request.return_value = response

        decorated = check_cors(lambda: _make_response_with_headers())
        result = decorated()

        headers = dict(result.headers.items())
        assert headers == {"Access-Control-Allow-Origin": "http://google.com"}
        assert headers["Access-Control-Allow-Origin"] == "http://google.com"
        assert result.headers["Access-Control-Allow-Origin"] == "http://google.com"


class TestCheckCorsDecoratedWithCorsEnabled:
    def test_no_allowed_domains(self, mock_app, mock_cors_deps: MockCorsDeps):
        response = MagicMock(
            headers={
                "Referer": "https://com.net",
                "Origin": "http://z.wikipedia.org",
            },
            host_url="http://localhost",
        )
        mock_app.config["CORS_DISABLED"] = False
        mock_cors_deps.load_request.return_value = response
        mock_cors_deps.get_allowed_domains.return_value = []

        decorated = check_cors(lambda: _make_response_with_headers())
        result = decorated()
        headers = dict(result.headers.items())
        assert result.status_code == 403
        assert headers == {
            "Content-Length": "110",
            "Content-Type": "application/json",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Max-Age": "86400",
        }

    def test_basics_403(self, mock_app, mock_cors_deps: MockCorsDeps):
        response = MagicMock(
            headers={
                "Referer": "https://google.com",
                "Origin": "http://google.com",
            },
            host_url="https://books.google.com",
        )
        mock_app.config["CORS_DISABLED"] = False
        mock_cors_deps.load_request.return_value = response

        decorated = check_cors(lambda: _make_response_with_headers())
        result = decorated()
        assert result.status_code == 403
        headers = dict(result.headers.items())
        assert headers == {
            "Content-Length": "110",
            "Content-Type": "application/json",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Max-Age": "86400",
        }

    def test_basics_200(self, mock_app, mock_cors_deps: MockCorsDeps):
        response = MagicMock(
            headers={
                "Referer": "https://google.com/test#new",
                "Origin": "ftp://z.com/test?q=/test#new",
            },
            host_url="https://ar.wikipedia.org",
        )
        mock_app.config["CORS_DISABLED"] = False
        mock_cors_deps.load_request.return_value = response
        mock_cors_deps.get_allowed_domains.return_value = ["z.com"]

        decorated = check_cors(lambda: _make_response_with_headers())
        result = decorated()
        headers = dict(result.headers.items())
        assert headers == {"Access-Control-Allow-Origin": "ftp://z.com"}

    def test_basics_same_host_url(self, mock_app, mock_cors_deps: MockCorsDeps):
        response = MagicMock(
            headers={
                "Referer": "https://com.net",
                "Origin": "http://z.wikipedia.org",
            },
            host_url="http://localhost",
        )
        mock_app.config["CORS_DISABLED"] = False
        mock_cors_deps.load_request.return_value = response
        mock_cors_deps.get_allowed_domains.return_value = ["z.com.net", "z.wikipedia.org"]

        decorated = check_cors(lambda: _make_response_with_headers())
        result = decorated()
        headers = dict(result.headers.items())
        # assert result.status_code == 200
        assert headers == {"Access-Control-Allow-Origin": "http://z.wikipedia.org"}
