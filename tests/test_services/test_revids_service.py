"""Tests for services.revids_service module."""

import pytest
from unittest.mock import patch, MagicMock


class TestGetRevid:
    """Tests for get_revid function."""

    def test_returns_empty_string_when_file_not_found(self):
        """Test that empty string is returned when file doesn't exist."""
        from src.app_main.services.revids_service import get_revid

        result = get_revid("Nonexistent Page")
        assert result == ""

    def test_returns_empty_string_when_title_not_in_file(self):
        """Test that empty string is returned when title is not in the file."""
        with patch("builtins.open", MagicMock(side_effect=FileNotFoundError)):
            from src.app_main.services.revids_service import get_revid

            result = get_revid("Nonexistent Page")
            assert result == ""


class TestGetRevidDb:
    """Tests for get_revid_db function."""

    def test_returns_empty_string_on_error(self):
        """Test that empty string is returned on error."""
        with patch("src.app.services.revids_service.requests") as mock_requests:
            mock_requests.get.side_effect = Exception("Network error")

            from src.app_main.services.revids_service import get_revid_db

            result = get_revid_db("Some Page")
            assert result == ""

    def test_returns_revid_on_success(self):
        """Test that revid is returned on success."""
        with patch("src.app.services.revids_service.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "results": [{"title": "Test Page", "revid": 12345}]
            }
            mock_requests.get.return_value = mock_response

            from src.app_main.services.revids_service import get_revid_db

            result = get_revid_db("Test Page")
            assert result == "12345"
