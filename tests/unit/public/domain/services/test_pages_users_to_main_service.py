"""
Unit tests for domain/services/pages_users_to_main_service.py module.

Tests for pages_users_to_main service layer which provides cached access to PagesUsersToMainDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.pages_users_to_main_service import (
    add_pages_users_to_main,
    delete_pages_users_to_main,
    get_pages_users_to_main,
    get_pages_users_to_main_db,
    list_pages_users_to_main,
    update_pages_users_to_main,
)


class TestGetPagesUsersToMainDb:
    """Tests for get_pages_users_to_main_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr(
            "src.app_main.public.domain.services.pages_users_to_main_service._PAGES_USERS_TO_MAIN_STORE", mock_db
        )
        monkeypatch.setattr(
            "src.app_main.public.domain.services.pages_users_to_main_service.has_db_config", lambda: True
        )

        result = get_pages_users_to_main_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr(
            "src.app_main.public.domain.services.pages_users_to_main_service._PAGES_USERS_TO_MAIN_STORE", None
        )
        monkeypatch.setattr(
            "src.app_main.public.domain.services.pages_users_to_main_service.has_db_config", lambda: False
        )

        with pytest.raises(RuntimeError, match="PagesUsersToMainDB requires database configuration"):
            get_pages_users_to_main_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new PagesUsersToMainDB is created when none cached."""
        monkeypatch.setattr(
            "src.app_main.public.domain.services.pages_users_to_main_service._PAGES_USERS_TO_MAIN_STORE", None
        )
        monkeypatch.setattr(
            "src.app_main.public.domain.services.pages_users_to_main_service.has_db_config", lambda: True
        )

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.pages_users_to_main_service.PagesUsersToMainDB") as MockDB:
            MockDB.return_value = mock_db_instance

            result = get_pages_users_to_main_db()

            assert result is mock_db_instance


class TestListPagesUsersToMain:
    """Tests for list_pages_users_to_main function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.pages_users_to_main_service.get_pages_users_to_main_db",
            lambda: mock_store,
        )

        result = list_pages_users_to_main()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestGetPagesUsersToMain:
    """Tests for get_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.pages_users_to_main_service.get_pages_users_to_main_db",
            lambda: mock_store,
        )

        result = get_pages_users_to_main(123)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(123)


class TestAddPagesUsersToMain:
    """Tests for add_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.pages_users_to_main_service.get_pages_users_to_main_db",
            lambda: mock_store,
        )

        result = add_pages_users_to_main(new_target="TestPage", new_user="TestUser", new_qid="Q123")

        assert result is mock_record
        mock_store.add.assert_called_once_with("TestPage", "TestUser", "Q123")


class TestUpdatePagesUsersToMain:
    """Tests for update_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.pages_users_to_main_service.get_pages_users_to_main_db",
            lambda: mock_store,
        )

        result = update_pages_users_to_main(1, new_qid="Q456")

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, new_qid="Q456")


class TestDeletePagesUsersToMain:
    """Tests for delete_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.pages_users_to_main_service.get_pages_users_to_main_db",
            lambda: mock_store,
        )

        result = delete_pages_users_to_main(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)
