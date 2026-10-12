"""Tests for cors module."""

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from src.main_app.services.core.cors import is_allowed

pytestmark = pytest.mark.unit


@dataclass
class MockCorsModuleDeps:
    request: MagicMock
    current_app: MagicMock
    app_settings: MagicMock


@pytest.fixture
def mock_request(mocker) -> MockCorsModuleDeps:
    """Fixture to mock Flask's request, current_app, and app_settings."""
    mock_req = MagicMock()
    mock_req.host_url = "https://mysite.com/"
    mock_req.headers = {}

    mocker.patch("src.main_app.services.core.cors.request", mock_req)

    mock_app = MagicMock()
    mock_app.config = {"CORS_DISABLED": False}
    mocker.patch("src.main_app.services.core.cors.is_allowed_checker.current_app", mock_app)

    mock_settings = MagicMock()
    mock_settings.cors.allowed_domains = ["trusted.com", "api.partner.net"]
    mocker.patch("src.main_app.services.core.cors.is_allowed_checker.app_settings", mock_settings)

    return MockCorsModuleDeps(
        request=mock_req,
        current_app=mock_app,
        app_settings=mock_settings,
    )


class TestCORSValidation:
    @pytest.mark.parametrize(
        "headers, expected",
        [
            # Allowed
            ({"Origin": "sip://mysite.com"}, "sip://mysite.com"),
            ({"Origin": "ftp://trusted.com"}, "ftp://trusted.com"),
            ({"Referer": "http://api.partner.net/dashboard"}, "http://api.partner.net"),
            # Denied
            ({"Origin": "https://trusted.com.attacker.com"}, None),
            ({"Origin": "https://nottrusted.com"}, None),
            ({"Origin": "https://sub.trusted.com"}, None),
            ({}, "https://mysite.com"),
        ],
    )
    def test_cors_validation(self, mock_request: MockCorsModuleDeps, headers, expected):
        mock_request.request.headers = headers
        assert is_allowed(mock_request.request) == expected

    def test_disabled_cors_bypass(self, mock_request: MockCorsModuleDeps):
        """Should allow everything if CORS_DISABLED is True."""
        mock_request.current_app.config["CORS_DISABLED"] = True
        mock_request.request.headers = {"Origin": "https://unknown-site.com"}

        # When CORS is disabled, returns origin or "*"
        assert is_allowed(mock_request.request) == "https://unknown-site.com"
