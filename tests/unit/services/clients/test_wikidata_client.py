"""Tests for clients.wikidata_client module."""

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest


@dataclass
class MockWikidataClientDeps:
    get_record_by_title: MagicMock
    link_it: MagicMock


@pytest.fixture
def mock_wikidata_deps(monkeypatch: pytest.MonkeyPatch) -> MockWikidataClientDeps:
    """Fixture to bundle and set up common patches for wikidata client tests."""
    _client = "src.main_app.services.clients.wikidata_client"

    mock_get_record = MagicMock()
    mock_link_it = MagicMock()

    monkeypatch.setattr(f"{_client}.WikidataClient.get_record_by_title", mock_get_record)
    monkeypatch.setattr(f"{_client}.WikidataClient._link_it", mock_link_it)
    monkeypatch.setattr(f"{_client}.get_record_by_title", mock_get_record)

    return MockWikidataClientDeps(
        get_record_by_title=mock_get_record,
        link_it=mock_link_it,
    )


class TestGetQidForMdtitle:
    """Tests for get_qid_for_mdtitle function and WikidataClient."""

    def test_returns_qid_when_found(self, mock_wikidata_deps: MockWikidataClientDeps):
        """Test that QID is returned when found in database."""
        mock_db = MagicMock()
        mock_db.qid = "Q12345"
        mock_wikidata_deps.get_record_by_title.return_value = mock_db

        from src.main_app.services.clients.wikidata_client import WikidataClient

        result = WikidataClient.get_qid_for_mdtitle("Test Page")

        assert result == "Q12345"

    def test_returns_none_on_error(self, mock_wikidata_deps: MockWikidataClientDeps):
        """Test that None is returned on database error."""
        mock_db = MagicMock()
        mock_db.qid = None
        mock_db.fetch_query_safe.side_effect = Exception("Database error")
        mock_wikidata_deps.get_record_by_title.return_value = mock_db

        from src.main_app.services.clients.wikidata_client import WikidataClient

        result = WikidataClient.get_qid_for_mdtitle("Test Page")

        assert result is None


class TestLinkToWikidata:
    """Tests for link_to_wikidata function and WikidataClient."""

    def test_returns_success_on_successful_link(self, mock_wikidata_deps: MockWikidataClientDeps):
        """Test that success result is returned on successful link."""
        mock_wikidata_deps.get_record_by_title.return_value = MagicMock(qid="Q12345")
        mock_wikidata_deps.link_it.return_value = {"success": True}

        from src.main_app.services.clients.wikidata_client import WikidataClient

        result = WikidataClient.link_to_wikidata(
            "Source Page",
            "ar",
            "TestUser",
            "Target Page",
            "access_key",
            "access_secret",
        )

        assert result["result"] == "success"
        assert result["qid"] == "Q12345"

    def test_returns_error_when_no_credentials(self, mock_wikidata_deps: MockWikidataClientDeps):
        """Test that error is returned when no credentials provided."""
        mock_wikidata_deps.get_record_by_title.return_value = MagicMock(qid="Q12345")

        from src.main_app.services.clients.wikidata_client import WikidataClient

        result = WikidataClient.link_to_wikidata(
            "Source Page",
            "ar",
            "TestUser",
            "Target Page",
            "",  # Empty access_key
            "",  # Empty access_secret
        )

        assert "error" in result
        assert "Access credentials not found" in result["error"]

    def test_returns_link_error_with_qid(self, mock_wikidata_deps: MockWikidataClientDeps):
        """Test that link error includes QID."""
        mock_wikidata_deps.get_record_by_title.return_value = MagicMock(qid="Q12345")
        mock_wikidata_deps.link_it.return_value = {"error": {"code": "protectedpage"}}

        from src.main_app.services.clients.wikidata_client import WikidataClient

        result = WikidataClient.link_to_wikidata(
            "Source Page",
            "ar",
            "TestUser",
            "Target Page",
            "access_key",
            "access_secret",
        )

        assert "qid" in result
        assert result["qid"] == "Q12345"
