"""Tests for services.wikidata_client module."""

import pytest
from unittest.mock import patch, MagicMock


class TestGetQidForMdtitle:
    """Tests for get_qid_for_mdtitle function."""

    def test_returns_qid_when_found(self):
        """Test that QID is returned when found in database."""
        with patch("src.app.services.wikidata_client.get_db") as mock_get_db:
            mock_db = MagicMock()
            mock_db.fetch_query_safe.return_value = [{"qid": "Q12345"}]
            mock_get_db.return_value = mock_db

            from src.app_main.services.wikidata_client import get_qid_for_mdtitle

            result = get_qid_for_mdtitle("Test Page")

            assert result == "Q12345"

    def test_returns_none_when_not_found(self):
        """Test that None is returned when QID is not found."""
        with patch("src.app.services.wikidata_client.get_db") as mock_get_db:
            mock_db = MagicMock()
            mock_db.fetch_query_safe.return_value = []
            mock_get_db.return_value = mock_db

            from src.app_main.services.wikidata_client import get_qid_for_mdtitle

            result = get_qid_for_mdtitle("Nonexistent Page")

            assert result is None

    def test_returns_none_on_error(self):
        """Test that None is returned on database error."""
        with patch("src.app.services.wikidata_client.get_db") as mock_get_db:
            mock_db = MagicMock()
            mock_db.fetch_query_safe.side_effect = Exception("Database error")
            mock_get_db.return_value = mock_db

            from src.app_main.services.wikidata_client import get_qid_for_mdtitle

            result = get_qid_for_mdtitle("Test Page")

            assert result is None


class TestGetTitleInfo:
    """Tests for get_title_info function."""

    def test_returns_page_info_on_success(self):
        """Test that page info is returned on success."""
        with patch("src.app.services.wikidata_client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "query": {
                    "pages": [
                        {"pageid": 123, "title": "Test Page", "missing": False}
                    ]
                }
            }
            mock_requests.get.return_value = mock_response

            from src.app_main.services.wikidata_client import get_title_info

            result = get_title_info("Test Page", "en")

            assert result is not None
            assert result["pageid"] == 123
            assert result["title"] == "Test Page"

    def test_returns_none_on_error(self):
        """Test that None is returned on error."""
        with patch("src.app.services.wikidata_client.requests") as mock_requests:
            mock_requests.get.side_effect = Exception("Network error")

            from src.app_main.services.wikidata_client import get_title_info

            result = get_title_info("Test Page", "en")

            assert result is None


class TestLinkToWikidata:
    """Tests for link_to_wikidata function."""

    def test_returns_success_on_successful_link(self):
        """Test that success result is returned on successful link."""
        with patch("src.app.services.wikidata_client.get_qid_for_mdtitle") as mock_qid, \
             patch("src.app.services.wikidata_client._link_it") as mock_link:
            mock_qid.return_value = "Q12345"
            mock_link.return_value = {"success": True}

            from src.app_main.services.wikidata_client import link_to_wikidata

            result = link_to_wikidata(
                "Source Page",
                "ar",
                "TestUser",
                "Target Page",
                "access_key",
                "access_secret",
            )

            assert result["result"] == "success"
            assert result["qid"] == "Q12345"

    def test_returns_error_when_no_credentials(self):
        """Test that error is returned when no credentials provided."""
        with patch("src.app.services.wikidata_client.get_qid_for_mdtitle") as mock_qid:
            mock_qid.return_value = "Q12345"

            from src.app_main.services.wikidata_client import link_to_wikidata

            result = link_to_wikidata(
                "Source Page",
                "ar",
                "TestUser",
                "Target Page",
                "",  # Empty access_key
                "",  # Empty access_secret
            )

            assert "error" in result
            assert "Access credentials not found" in result["error"]

    def test_returns_link_error_with_qid(self):
        """Test that link error includes QID."""
        with patch("src.app.services.wikidata_client.get_qid_for_mdtitle") as mock_qid, \
             patch("src.app.services.wikidata_client._link_it") as mock_link:
            mock_qid.return_value = "Q12345"
            mock_link.return_value = {"error": {"code": "protectedpage"}}

            from src.app_main.services.wikidata_client import link_to_wikidata

            result = link_to_wikidata(
                "Source Page",
                "ar",
                "TestUser",
                "Target Page",
                "access_key",
                "access_secret",
            )

            assert "qid" in result
            assert result["qid"] == "Q12345"
