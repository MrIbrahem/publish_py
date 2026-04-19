"""Tests for clients.mediawiki_api module."""

from unittest.mock import MagicMock, patch

import pytest


class TestPublishDoEdit:
    """Tests for publish_do_edit function."""

    def test_returns_edit_result_on_success(self):
        """Test that edit result is returned on success."""
        with patch("src.sqlalchemy_app.shared.clients.mediawiki_api.post_params") as mock_post:
            mock_post.return_value = '{"edit": {"result": "Success", "newrevid": 12345}}'

            from src.sqlalchemy_app.shared.clients.mediawiki_api import publish_do_edit

            result = publish_do_edit(
                {"action": "edit", "title": "Test Page"},
                "en",
                "access_key",
                "access_secret",
            )

            assert result["edit"]["result"] == "Success"
            assert result["edit"]["newrevid"] == 12345

    def test_returns_error_on_failed_edit(self):
        """Test that error is returned on failed edit."""
        with patch("src.sqlalchemy_app.shared.clients.mediawiki_api.post_params") as mock_post:
            mock_post.return_value = '{"error": {"code": "protectedpage", "info": "Page is protected"}}'

            from src.sqlalchemy_app.shared.clients.mediawiki_api import publish_do_edit

            result = publish_do_edit(
                {"action": "edit", "title": "Protected Page"},
                "en",
                "access_key",
                "access_secret",
            )

            assert "error" in result
            assert result["error"]["code"] == "protectedpage"

    def test_returns_empty_dict_on_empty_response(self):
        """Test that empty dict is returned on empty response."""
        with patch("src.sqlalchemy_app.shared.clients.mediawiki_api.post_params") as mock_post:
            mock_post.return_value = ""

            from src.sqlalchemy_app.shared.clients.mediawiki_api import publish_do_edit

            result = publish_do_edit(
                {"action": "edit", "title": "Test Page"},
                "en",
                "access_key",
                "access_secret",
            )

            assert result == {}

    def test_returns_error_on_invalid_json(self):
        """Test that error is returned on invalid JSON response."""
        with patch("src.sqlalchemy_app.shared.clients.mediawiki_api.post_params") as mock_post:
            mock_post.return_value = "not valid json"

            from src.sqlalchemy_app.shared.clients.mediawiki_api import publish_do_edit

            result = publish_do_edit(
                {"action": "edit", "title": "Test Page"},
                "en",
                "access_key",
                "access_secret",
            )

            assert "error" in result

    def test_constructs_correct_domain_url(self):
        """Test that the correct domain URL is constructed."""
        with patch("src.sqlalchemy_app.shared.clients.mediawiki_api.post_params") as mock_post:
            mock_post.return_value = '{"edit": {"result": "Success"}}'

            from src.sqlalchemy_app.shared.clients.mediawiki_api import publish_do_edit

            publish_do_edit(
                {"action": "edit", "title": "Test Page"},
                "ar",
                "access_key",
                "access_secret",
            )

            # Verify the domain was passed correctly
            call_args = mock_post.call_args
            assert call_args[0][1] == "https://ar.wikipedia.org"


class TestGetTitleInfo:
    """Tests for get_title_info function."""

    def test_returns_page_info_on_success(self):
        """Test that page info is returned on success."""
        with patch("src.sqlalchemy_app.shared.clients.mediawiki_api.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "query": {"pages": [{"pageid": 123, "title": "Test Page", "missing": False}]}
            }
            mock_requests.get.return_value = mock_response

            from src.sqlalchemy_app.shared.clients.mediawiki_api import get_title_info

            result = get_title_info("Test Page", "en")

            assert result is not None
            assert result["pageid"] == 123
            assert result["title"] == "Test Page"

    def test_returns_none_on_error(self):
        """Test that None is returned on error."""
        with patch("src.sqlalchemy_app.shared.clients.mediawiki_api.requests") as mock_requests:
            mock_requests.get.side_effect = Exception("Network error")

            from src.sqlalchemy_app.shared.clients.mediawiki_api import get_title_info

            result = get_title_info("Test Page", "en")

            assert result is None
