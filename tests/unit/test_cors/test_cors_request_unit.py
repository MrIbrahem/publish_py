"""Tests for cors module."""

from unittest.mock import MagicMock

import pytest

from src.app_main.cors import is_allowed


@pytest.fixture
def mock_request(mocker):
    """Fixture to mock Flask's request and current_app."""
    mock_req = MagicMock()
    mock_req.host_url = "https://mysite.com/"
    mock_req.headers = {}

    mocker.patch("src.app_main.cors.request", mock_req)

    mock_app = MagicMock()
    mock_app.config = {"CORS_DISABLED": False}
    mocker.patch("src.app_main.cors.is_allowed_checker.current_app", mock_app)

    mock_settings = MagicMock()
    mock_settings.cors.allowed_domains = ["trusted.com", "api.partner.net"]
    mocker.patch("src.app_main.cors.is_allowed_checker.settings", mock_settings)

    return mock_req, mock_app


class TestCORSValidation:
    @pytest.mark.parametrize("headers, expected", [
        # Allowed
        ({"Origin": "https://mysite.com"}, "mysite.com"),
        ({"Origin": "https://trusted.com"}, "trusted.com"),
        ({"Referer": "https://api.partner.net/dashboard"}, "api.partner.net"),

        # Denied
        ({"Origin": "https://trusted.com.attacker.com"}, None),
        ({"Origin": "https://nottrusted.com"}, None),
        ({"Origin": "https://sub.trusted.com"}, None),
        ({}, None),
    ])
    def test_cors_validation(self, mock_request, headers, expected):
        mock_req, _ = mock_request
        mock_req.headers = headers
        assert is_allowed(mock_req) == expected

    def test_disabled_cors_bypass(self, mock_request):
        """Should allow everything if CORS_DISABLED is True."""
        mock_req, mock_app = mock_request
        mock_app.config["CORS_DISABLED"] = True
        mock_req.headers = {"Origin": "https://unknown-site.com"}

        # When CORS is disabled, returns origin or "*"
        assert is_allowed(mock_req) == "unknown-site.com"
