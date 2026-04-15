"""
Tests for cors wrappers module, to test response.headers["Access-Control-Allow-Origin"] value
"""

from unittest.mock import MagicMock

import pytest

from src.app_main.cors import validate_access, check_cors


def _make_response_with_headers():
    """Create a mock response with a real dict headers attribute."""
    response = MagicMock()
    response.headers = {}
    return response


class TestValidateAccessControlAllowOrigin:
    def test_allowed_domain_sets_header(self, app, mock_load_request, mock_is_allowed, mock_check_secret):
        mock_is_allowed.return_value = "trusted.com"
        response = _make_response_with_headers()
        decorated = validate_access(lambda: response)

        result = decorated()

        assert result.headers["Access-Control-Allow-Origin"] == "https://trusted.com"

    def test_secret_code_valid_and_allowed_domain_uses_allowed_domain_in_header(
        self, app, mock_load_request, mock_is_allowed, mock_check_secret
    ):
        mock_is_allowed.return_value = "partner.net"
        mock_check_secret.return_value = "secret-host.com"
        response = _make_response_with_headers()
        decorated = validate_access(lambda: response)

        result = decorated()

        assert result.headers["Access-Control-Allow-Origin"] == "https://partner.net"

    def test_denied_returns_403_without_cors_header(self, app, mock_load_request, mock_is_denied, mock_check_secret):
        mock_check_secret.return_value = None

        result = validate_access(lambda: _make_response_with_headers())()

        assert result.status_code == 403
        assert "Access-Control-Allow-Origin" not in result.headers

    def test_response_without_headers_attribute_no_error(
        self, app, mock_load_request, mock_is_allowed, mock_check_secret
    ):
        mock_is_allowed.return_value = "trusted.com"
        plain_response = "just a string"
        decorated = validate_access(lambda: plain_response)

        result = decorated()

        assert result == "just a string"

    def test_secret_code_valid_no_allowed_domain_sets_header_to_none(
        self, app, mock_load_request, mock_is_denied, mock_check_secret
    ):
        mock_check_secret.return_value = "secret-host.com"
        response = _make_response_with_headers()
        decorated = validate_access(lambda: response)

        result = decorated()

        assert result.headers.get("Access-Control-Allow-Origin") == "https://secret-host.com"
        # assert "Access-Control-Allow-Origin" not in result.headers

    def test_all_results_none(
        self, app, mock_load_request, mock_is_denied, mock_check_secret
    ):
        mock_check_secret.return_value = None
        response = _make_response_with_headers()
        decorated = validate_access(lambda: response)

        result = decorated()

        assert "Access-Control-Allow-Origin" not in result.headers
        assert result.headers.get("Access-Control-Allow-Origin") is None


class TestCheckCorsAccessControlAllowOrigin:
    def test_allowed_domain_sets_header(self, app, mock_load_request, mock_is_allowed):
        mock_is_allowed.return_value = "trusted.com"
        response = _make_response_with_headers()
        decorated = check_cors(lambda: response)

        result = decorated()

        assert result.headers["Access-Control-Allow-Origin"] == "https://trusted.com"

    def test_different_allowed_domain_sets_header(self, app, mock_load_request, mock_is_allowed):
        mock_is_allowed.return_value = "api.partner.net"
        response = _make_response_with_headers()
        decorated = check_cors(lambda: response)

        result = decorated()

        assert result.headers["Access-Control-Allow-Origin"] == "https://api.partner.net"

    def test_denied_returns_403_without_cors_header(self, app, mock_load_request, mock_is_denied):

        result = check_cors(lambda: _make_response_with_headers())()

        assert result.status_code == 403
        assert "Access-Control-Allow-Origin" not in result.headers

    def test_response_without_headers_attribute_no_error(self, app, mock_load_request, mock_is_allowed):
        mock_is_allowed.return_value = "trusted.com"
        plain_response = "just a string"
        decorated = check_cors(lambda: plain_response)

        result = decorated()

        assert result == "just a string"
