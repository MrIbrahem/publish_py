"""
Unit tests for qids_service module.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.shared.domain.services.qids_service import (
    add_qid,
    delete_qid,
    get_page_qid,
    get_qids_db,
    get_title_to_qid,
    list_qids,
    update_qid,
)


class TestGetQidsDb:
    """Tests for get_qids_db function."""

    def test_returns_cached_instance_on_subsequent_calls(self, monkeypatch):
        """Test that the same instance is returned on multiple calls."""
        mock_store = MagicMock()
        monkeypatch.setattr("src.app_main.shared.domain.services.qids_service._qid_STORE", mock_store)

        result1 = get_qids_db()
        result2 = get_qids_db()

        assert result1 is result2
        assert result1 is mock_store

    def test_raises_error_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when database config is missing."""
        monkeypatch.setattr("src.app_main.shared.domain.services.qids_service.has_db_config", lambda: False)
        monkeypatch.setattr("src.app_main.shared.domain.services.qids_service._qid_STORE", None)

        with pytest.raises(RuntimeError, match="QidsDB requires database configuration"):
            get_qids_db()


class TestGetPageQid:
    """Tests for get_page_qid function."""

    def test_returns_qid_record(self, monkeypatch):
        """Test that function returns a QidRecord."""
        mock_store = MagicMock()
        mock_qid = MagicMock()
        mock_store.fetch_by_title.return_value = mock_qid
        monkeypatch.setattr("src.app_main.shared.domain.services.qids_service.get_qids_db", lambda: mock_store)

        result = get_page_qid("TestArticle")

        assert result is mock_qid
        mock_store.fetch_by_title.assert_called_once_with("TestArticle")

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when QID not found."""
        mock_store = MagicMock()
        mock_store.fetch_by_title.return_value = None
        monkeypatch.setattr("src.app_main.shared.domain.services.qids_service.get_qids_db", lambda: mock_store)

        result = get_page_qid("NonExistentArticle")

        assert result is None


class TestAddQid:
    """Tests for add_qid function."""

    def test_adds_qid_and_returns_record(self, monkeypatch):
        """Test that add_qid adds a QID and returns the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr("src.app_main.shared.domain.services.qids_service.get_qids_db", lambda: mock_store)

        result = add_qid("TestArticle", "Q12345")

        mock_store.add.assert_called_once_with("TestArticle", "Q12345")
        assert result is mock_record


class TestUpdateQid:
    """Tests for update_qid function."""

    def test_updates_qid_and_returns_record(self, monkeypatch):
        """Test that update_qid updates and returns the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr("src.app_main.shared.domain.services.qids_service.get_qids_db", lambda: mock_store)

        result = update_qid(1, "UpdatedArticle", "Q99999")

        mock_store.update.assert_called_once_with(1, "UpdatedArticle", "Q99999")
        assert result is mock_record


class TestDeleteQid:
    """Tests for delete_qid function."""

    def test_deletes_qid(self, monkeypatch):
        """Test that delete_qid calls store delete."""
        mock_store = MagicMock()
        monkeypatch.setattr("src.app_main.shared.domain.services.qids_service.get_qids_db", lambda: mock_store)

        delete_qid(1)

        mock_store.delete.assert_called_once_with(1)


class TestListQids:
    """Tests for list_qids function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_qids returns all records."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr("src.app_main.shared.domain.services.qids_service.get_qids_db", lambda: mock_store)

        result = list_qids()

        assert result == mock_records
        mock_store.list.assert_called_once()

    def test_returns_empty_list_when_no_records(self, monkeypatch):
        """Test that list_qids returns empty list when no records exist."""
        mock_store = MagicMock()
        mock_store.list.return_value = []
        monkeypatch.setattr("src.app_main.shared.domain.services.qids_service.get_qids_db", lambda: mock_store)

        result = list_qids()

        assert result == []


class TestGetTitleToQid:
    """Tests for get_title_to_qid function."""

    def test_returns_title_to_qid_mapping(self, monkeypatch):
        """Test that get_title_to_qid returns correct mapping."""
        mock_record1 = MagicMock()
        mock_record1.title = "Article1"
        mock_record1.qid = "Q12345"

        mock_record2 = MagicMock()
        mock_record2.title = "Article2"
        mock_record2.qid = "Q67890"

        mock_store = MagicMock()
        mock_store.list.return_value = [mock_record1, mock_record2]
        monkeypatch.setattr("src.app_main.shared.domain.services.qids_service.get_qids_db", lambda: mock_store)

        result = get_title_to_qid()

        assert result == {"Article1": "Q12345", "Article2": "Q67890"}

    def test_handles_empty_qid(self, monkeypatch):
        """Test that get_title_to_qid handles empty QID values."""
        mock_record = MagicMock()
        mock_record.title = "Article1"
        mock_record.qid = None

        mock_store = MagicMock()
        mock_store.list.return_value = [mock_record]
        monkeypatch.setattr("src.app_main.shared.domain.services.qids_service.get_qids_db", lambda: mock_store)

        result = get_title_to_qid()

        assert result == {"Article1": ""}
