"""
Tests for cors wrappers module, to test response.headers["Access-Control-Allow-Origin"] value
"""

from unittest.mock import MagicMock

import pytest
from pytest_flask.plugin import JSONResponse

from src.app_main.cors import validate_access, check_cors


def _make_response_with_headers() -> MagicMock:
    """Create a mock response with a real dict headers attribute."""
    response = MagicMock()
    response.headers = {}
    return response


class TestCheckCorsDecoratedWithCorsDisabled:
    def test_basics_empty_headers(self, mocker, app):
        response = MagicMock(
            headers={
                "Referer": "",
                "Origin": "",
            },
            host_url="",
        )
        app.config["CORS_DISABLED"] = True
        mocker.patch("src.app_main.cors._load_request", return_value=response)

        decorated = check_cors(lambda: _make_response_with_headers())
        result = decorated()

        assert result.headers["Access-Control-Allow-Origin"] == "https://*"

    def test_with_headers(self, mocker, app):
        response = MagicMock(
            headers={
                "Referer": "https://google.com",
                "Origin": "http://google.com",
            },
            host_url="https://books.google.com",
        )
        app.config["CORS_DISABLED"] = True
        mocker.patch("src.app_main.cors._load_request", return_value=response)

        decorated = check_cors(lambda: _make_response_with_headers())
        result = decorated()

        headers = dict(result.headers.items())
        assert headers == {"Access-Control-Allow-Origin": "http://google.com"}
        assert headers["Access-Control-Allow-Origin"] == "http://google.com"
        assert result.headers["Access-Control-Allow-Origin"] == "http://google.com"


class TestCheckCorsDecoratedWithCorsEnabled:
    def test_no_allowed_domains(self, mocker, app):
        response = MagicMock(
            headers={
                "Referer": "https://com.net",
                "Origin": "http://z.wikipedia.org",
            },
            host_url="http://localhost",
        )
        app.config["CORS_DISABLED"] = False
        mocker.patch("src.app_main.cors._load_request", return_value=response)
        mocker.patch("src.app_main.cors.is_allowed_checker._get_allowed_domains", return_value=[])

        decorated = check_cors(lambda: _make_response_with_headers())
        result = decorated()
        headers = dict(result.headers.items())
        assert result.status_code == 403
        assert headers == {"Content-Length": "110", "Content-Type": "application/json"}

    def test_basics_403(self, mocker, app):
        response = MagicMock(
            headers={
                "Referer": "https://google.com",
                "Origin": "http://google.com",
            },
            host_url="https://books.google.com",
        )
        app.config["CORS_DISABLED"] = False
        mocker.patch("src.app_main.cors._load_request", return_value=response)

        decorated = check_cors(lambda: _make_response_with_headers())
        result = decorated()
        assert result.status_code == 403
        headers = dict(result.headers.items())
        assert headers == {"Content-Length": "110", "Content-Type": "application/json"}

    def test_basics_200(self, mocker, app):
        response = MagicMock(
            headers={
                "Referer": "https://google.com/test#new",
                "Origin": "ftp://z.com/test?q=/test#new",
            },
            host_url="https://ar.wikipedia.org",
        )
        app.config["CORS_DISABLED"] = False
        mocker.patch("src.app_main.cors._load_request", return_value=response)
        mocker.patch("src.app_main.cors.is_allowed_checker._get_allowed_domains", return_value=["z.com"])

        decorated = check_cors(lambda: _make_response_with_headers())
        result = decorated()
        headers = dict(result.headers.items())
        assert headers == {"Access-Control-Allow-Origin": "ftp://z.com"}

    def test_basics_same_host_url(self, mocker, app):
        response = MagicMock(
            headers={
                "Referer": "https://com.net",
                "Origin": "http://z.wikipedia.org",
            },
            host_url="http://localhost",
        )
        app.config["CORS_DISABLED"] = False
        mocker.patch("src.app_main.cors._load_request", return_value=response)
        mocker.patch("src.app_main.cors.is_allowed_checker._get_allowed_domains", return_value=["z.com.net", "z.wikipedia.org"])

        decorated = check_cors(lambda: _make_response_with_headers())
        result = decorated()
        headers = dict(result.headers.items())
        # assert result.status_code == 200
        assert headers == {"Access-Control-Allow-Origin": "http://z.wikipedia.org"}
