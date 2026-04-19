"""
Unit tests for domain/services/mdwiki_revid_service.py module.

Tests for mdwiki_revids service layer which provides cached access to MdwikiRevidsDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.mdwiki_revid_service import (
    add_mdwiki_revid,
    add_or_update_mdwiki_revid,
    delete_mdwiki_revid,
    get_mdwiki_revid_by_title,
    get_mdwiki_revids_db,
    get_revid_for_title,
    list_mdwiki_revids,
    update_mdwiki_revid,
)


class TestGetMdwikiRevidsDb:
    """Tests for get_mdwiki_revids_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.services.mdwiki_revid_service._MDWIKI_REVIDS_STORE", mock_db)
        monkeypatch.setattr("src.app_main.public.domain.services.mdwiki_revid_service.has_db_config", lambda: True)

        result = get_mdwiki_revids_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr("src.app_main.public.domain.services.mdwiki_revid_service._MDWIKI_REVIDS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.mdwiki_revid_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="MdwikiRevidsDB requires database configuration"):
            get_mdwiki_revids_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new MdwikiRevidsDB is created when none cached."""
        monkeypatch.setattr("src.app_main.public.domain.services.mdwiki_revid_service._MDWIKI_REVIDS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.mdwiki_revid_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.mdwiki_revid_service.MdwikiRevidsDB") as MockDB:
            MockDB.return_value = mock_db_instance

            result = get_mdwiki_revids_db()

            assert result is mock_db_instance


class TestListMdwikiRevids:
    """Tests for list_mdwiki_revids function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.mdwiki_revid_service.get_mdwiki_revids_db", lambda: mock_store
        )

        result = list_mdwiki_revids()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestGetMdwikiRevidByTitle:
    """Tests for get_mdwiki_revid_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_title."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.mdwiki_revid_service.get_mdwiki_revids_db", lambda: mock_store
        )

        result = get_mdwiki_revid_by_title("TestPage")

        assert result is mock_record
        mock_store.fetch_by_title.assert_called_once_with("TestPage")


class TestAddMdwikiRevid:
    """Tests for add_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.mdwiki_revid_service.get_mdwiki_revids_db", lambda: mock_store
        )

        result = add_mdwiki_revid("TestPage", 12345)

        assert result is mock_record
        mock_store.add.assert_called_once_with("TestPage", 12345)


class TestAddOrUpdateMdwikiRevid:
    """Tests for add_or_update_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.mdwiki_revid_service.get_mdwiki_revids_db", lambda: mock_store
        )

        result = add_or_update_mdwiki_revid("TestPage", 54321)

        assert result is mock_record
        mock_store.add_or_update.assert_called_once_with("TestPage", 54321)


class TestUpdateMdwikiRevid:
    """Tests for update_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.mdwiki_revid_service.get_mdwiki_revids_db", lambda: mock_store
        )

        result = update_mdwiki_revid("TestPage", 54321)

        assert result is mock_record
        mock_store.update.assert_called_once_with("TestPage", 54321)


class TestDeleteMdwikiRevid:
    """Tests for delete_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.mdwiki_revid_service.get_mdwiki_revids_db", lambda: mock_store
        )

        result = delete_mdwiki_revid("TestPage")

        assert result is mock_record
        mock_store.delete.assert_called_once_with("TestPage")


class TestGetRevidForTitle:
    """Tests for get_revid_for_title function."""

    def test_returns_revid_when_record_exists(self, monkeypatch):
        """Test that function returns revid when record found."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.revid = 12345
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.mdwiki_revid_service.get_mdwiki_revids_db", lambda: mock_store
        )

        result = get_revid_for_title("TestPage")

        assert result == 12345

    def test_returns_none_when_record_not_found(self, monkeypatch):
        """Test that function returns None when record not found."""
        mock_store = MagicMock()
        mock_store.fetch_by_title.return_value = None
        monkeypatch.setattr(
            "src.app_main.public.domain.services.mdwiki_revid_service.get_mdwiki_revids_db", lambda: mock_store
        )

        result = get_revid_for_title("Missing")

        assert result is None
