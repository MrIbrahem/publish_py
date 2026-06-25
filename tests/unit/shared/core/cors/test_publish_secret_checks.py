"""Unit tests for cors.publish_secret_checks module.

Tests for publish secret code verification.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.main_app.shared.core.cors.publish_secret_checks import (
    _get_publish_secret_code,
    check_publish_secret_code,
)


class TestGetPublishSecretCode:
    """Tests for _get_publish_secret_code function."""

    def test_returns_secret_from_settings(self, monkeypatch):
        """Test that secret is retrieved from settings."""
        mock_settings = MagicMock()
        mock_settings.security.publish_secret_code = "my_secret_code"

        monkeypatch.setattr("src.main_app.shared.core.cors.publish_secret_checks.settings", mock_settings)

        result = _get_publish_secret_code()

        assert result == "my_secret_code"

    def test_returns_empty_string_when_not_set(self, monkeypatch):
        """Test that empty string is returned when not set."""
        mock_settings = MagicMock()
        mock_settings.security.publish_secret_code = ""

        monkeypatch.setattr("src.main_app.shared.core.cors.publish_secret_checks.settings", mock_settings)

        result = _get_publish_secret_code()

        assert result == ""


class TestCheckPublishSecretCode:
    """Tests for check_publish_secret_code function."""

    def test_returns_none_when_no_secret_configured(self, mock_app, monkeypatch):
        """Test that None is returned when no secret is configured."""
        monkeypatch.setattr("src.main_app.shared.core.cors.publish_secret_checks._get_publish_secret_code", lambda: "")

        with mock_app.test_request_context():
            result = check_publish_secret_code()

            assert result is None

    def test_returns_none_when_no_header_present(self, mock_app, monkeypatch):
        """Test that None is returned when X-Secret-Key header is missing."""
        monkeypatch.setattr(
            "src.main_app.shared.core.cors.publish_secret_checks._get_publish_secret_code",
            lambda: "expected_secret",
        )

        with mock_app.test_request_context():
            result = check_publish_secret_code()

            assert result is None

    def test_returns_none_when_header_does_not_match(self, mock_app, monkeypatch):
        """Test that None is returned when header value does not match."""
        monkeypatch.setattr(
            "src.main_app.shared.core.cors.publish_secret_checks._get_publish_secret_code",
            lambda: "expected_secret",
        )

        with mock_app.test_request_context(headers={"X-Secret-Key": "wrong_secret"}):
            result = check_publish_secret_code()

            assert result is None

    def test_returns_host_when_header_matches(self, mock_app, monkeypatch):
        """Test that host is returned when header value matches."""
        monkeypatch.setattr(
            "src.main_app.shared.core.cors.publish_secret_checks._get_publish_secret_code",
            lambda: "correct_secret",
        )

        with mock_app.test_request_context(headers={"X-Secret-Key": "correct_secret", "Origin": "https://example.com"}):
            result = check_publish_secret_code()

            assert result == "example.com"

    def test_uses_request_host_when_origin_missing(self, mock_app, monkeypatch):
        """Test that request host is used when Origin header is missing."""
        monkeypatch.setattr(
            "src.main_app.shared.core.cors.publish_secret_checks._get_publish_secret_code",
            lambda: "correct_secret",
        )

        with mock_app.test_request_context(headers={"X-Secret-Key": "correct_secret"}, base_url="https://api.example.com"):
            result = check_publish_secret_code()

            assert "example.com" in result

    def test_uses_timing_safe_comparison(self, mock_app, monkeypatch):
        """Test that timing-safe comparison is used (hmac.compare_digest)."""
        monkeypatch.setattr(
            "src.main_app.shared.core.cors.publish_secret_checks._get_publish_secret_code", lambda: "secret"
        )

        with patch("src.main_app.shared.core.cors.publish_secret_checks.hmac.compare_digest") as mock_compare:
            mock_compare.return_value = True

            with mock_app.test_request_context(headers={"X-Secret-Key": "secret"}):
                check_publish_secret_code()

                mock_compare.assert_called_once_with("secret", "secret")
