"""
Unit tests for domain/services/refs_count_service.py module.

Tests for refs_counts service layer which provides cached access to RefsCountsDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.refs_count_service import (
    add_or_update_refs_count,
    add_refs_count,
    delete_refs_count,
    get_ref_counts_for_title,
    get_refs_count,
    get_refs_count_by_title,
    get_refs_counts_db,
    list_refs_counts,
    update_refs_count,
)


class TestGetRefsCountsDb:
    """Tests for get_refs_counts_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.services.refs_count_service._REFS_COUNTS_STORE", mock_db)
        monkeypatch.setattr("src.app_main.public.domain.services.refs_count_service.has_db_config", lambda: True)

        result = get_refs_counts_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr("src.app_main.public.domain.services.refs_count_service._REFS_COUNTS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.refs_count_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="RefsCountsDB requires database configuration"):
            get_refs_counts_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new RefsCountsDB is created when none cached."""
        monkeypatch.setattr("src.app_main.public.domain.services.refs_count_service._REFS_COUNTS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.refs_count_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.refs_count_service.RefsCountsDB") as MockDB:
            MockDB.return_value = mock_db_instance

            result = get_refs_counts_db()

            assert result is mock_db_instance


class TestListRefsCounts:
    """Tests for list_refs_counts function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.refs_count_service.get_refs_counts_db", lambda: mock_store
        )

        result = list_refs_counts()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestGetRefsCount:
    """Tests for get_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.refs_count_service.get_refs_counts_db", lambda: mock_store
        )

        result = get_refs_count(123)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(123)


class TestGetRefsCountByTitle:
    """Tests for get_refs_count_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_title."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.refs_count_service.get_refs_counts_db", lambda: mock_store
        )

        result = get_refs_count_by_title("TestPage")

        assert result is mock_record
        mock_store.fetch_by_title.assert_called_once_with("TestPage")


class TestAddRefsCount:
    """Tests for add_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.refs_count_service.get_refs_counts_db", lambda: mock_store
        )

        result = add_refs_count("TestPage", r_lead_refs=5, r_all_refs=20)

        assert result is mock_record
        mock_store.add.assert_called_once_with("TestPage", 5, 20)


class TestAddOrUpdateRefsCount:
    """Tests for add_or_update_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add_or_update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.refs_count_service.get_refs_counts_db", lambda: mock_store
        )

        result = add_or_update_refs_count("TestPage", r_lead_refs=10, r_all_refs=40)

        assert result is mock_record
        mock_store.add_or_update.assert_called_once_with("TestPage", 10, 40)


class TestUpdateRefsCount:
    """Tests for update_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.refs_count_service.get_refs_counts_db", lambda: mock_store
        )

        result = update_refs_count(1, r_lead_refs=10, r_all_refs=40)

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, r_lead_refs=10, r_all_refs=40)


class TestDeleteRefsCount:
    """Tests for delete_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.refs_count_service.get_refs_counts_db", lambda: mock_store
        )

        result = delete_refs_count(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)


class TestGetRefsCountsForTitle:
    """Tests for get_ref_counts_for_title function."""

    def test_returns_counts_when_record_exists(self, monkeypatch):
        """Test that function returns counts when record found."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.r_lead_refs = 5
        mock_record.r_all_refs = 20
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.refs_count_service.get_refs_counts_db", lambda: mock_store
        )

        lead, all_refs = get_ref_counts_for_title("TestPage")

        assert lead == 5
        assert all_refs == 20

    def test_returns_none_when_record_not_found(self, monkeypatch):
        """Test that function returns None when record not found."""
        mock_store = MagicMock()
        mock_store.fetch_by_title.return_value = None
        monkeypatch.setattr(
            "src.app_main.public.domain.services.refs_count_service.get_refs_counts_db", lambda: mock_store
        )

        lead, all_refs = get_ref_counts_for_title("Missing")

        assert lead is None
        assert all_refs is None
