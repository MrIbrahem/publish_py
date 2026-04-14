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
    mocker.patch("src.app_main.cors.current_app", mock_app)

    mock_settings = MagicMock()
    mock_settings.cors.allowed_domains = ["trusted.com", "api.partner.net"]
    mocker.patch("src.app_main.cors.settings", mock_settings)

    return mock_req, mock_app


class TestCORSValidation:
    def test_allowed_same_origin(self, mock_request):
        """Should allow if Origin matches host_url exactly."""
        mock_req, _ = mock_request
        mock_req.headers = {"Origin": "https://mysite.com"}
        assert is_allowed() == "https://mysite.com"

    def test_allowed_configured_domain(self, mock_request):
        """Should allow if Origin is in the allowed_domains list."""
        mock_req, _ = mock_request
        mock_req.headers = {"Origin": "https://trusted.com"}
        # is_allowed() returns the domain string from allowed_domains, not the URL
        assert is_allowed() == "trusted.com"

    def test_denied_malicious_suffix(self, mock_request):
        """
        SECURITY TEST: Should deny if trusted domain is just a prefix.
        Example: trusted.com.attacker.com
        """
        mock_req, _ = mock_request
        mock_req.headers = {"Origin": "https://trusted.com.attacker.com"}
        assert is_allowed() is None

    def test_denied_malicious_prefix(self, mock_request):
        """
        SECURITY TEST: Should deny if trusted domain is part of a longer name.
        Example: NOTtrusted.com
        """
        mock_req, _ = mock_request
        mock_req.headers = {"Origin": "https://nottrusted.com"}
        assert is_allowed() is None

    def test_allowed_referer_fallback(self, mock_request):
        """Should allow if Referer is valid even if Origin is missing."""
        mock_req, _ = mock_request
        mock_req.headers = {"Referer": "https://api.partner.net/dashboard"}
        # is_allowed() returns the matched domain from allowed_domains, not the full URL
        assert is_allowed() == "api.partner.net"

    def test_disabled_cors_bypass(self, mock_request):
        """Should allow everything if CORS_DISABLED is True."""
        mock_req, mock_app = mock_request
        mock_app.config["CORS_DISABLED"] = True
        mock_req.headers = {"Origin": "https://unknown-site.com"}

        # When CORS is disabled, returns origin or "*"
        assert is_allowed() == "https://unknown-site.com"

    def test_no_headers_denied(self, mock_request):
        """Should deny if both Origin and Referer are missing."""
        mock_req, _ = mock_request
        mock_req.headers = {}
        assert is_allowed() is None

    def test_subdomain_denied_if_not_explicit(self, mock_request):
        """Should deny subdomains if only the root is allowed (Exact Match)."""
        mock_req, _ = mock_request
        mock_req.headers = {"Origin": "https://sub.trusted.com"}
        # Since we are doing '==' comparison on netloc
        assert is_allowed() is None
