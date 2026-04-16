"""
Unit tests for admin/domain/services/users_no_inprocess_service.py module.

Tests for users_no_inprocess service layer which provides cached access to UsersNoInprocessDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.admin.domain.services.users_no_inprocess_service import (
    add_or_update_users_no_inprocess,
    add_users_no_inprocess,
    delete_users_no_inprocess,
    get_users_no_inprocess,
    get_users_no_inprocess_by_user,
    get_users_no_inprocess_db,
    list_active_users_no_inprocess,
    list_users_no_inprocess,
    should_hide_from_inprocess,
    update_users_no_inprocess,
)


class TestGetUsersNoInprocessDb:
    """Tests for get_users_no_inprocess_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service._USERS_NO_INPROCESS_STORE", mock_db
        )
        monkeypatch.setattr("src.app_main.admin.domain.services.users_no_inprocess_service.has_db_config", lambda: True)

        result = get_users_no_inprocess_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service._USERS_NO_INPROCESS_STORE", None
        )
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service.has_db_config", lambda: False
        )

        with pytest.raises(RuntimeError, match="UsersNoInprocessDB requires database configuration"):
            get_users_no_inprocess_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new UsersNoInprocessDB is created when none cached."""
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service._USERS_NO_INPROCESS_STORE", None
        )
        monkeypatch.setattr("src.app_main.admin.domain.services.users_no_inprocess_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.admin.domain.services.users_no_inprocess_service.UsersNoInprocessDB") as MockDB:
            MockDB.return_value = mock_db_instance

            result = get_users_no_inprocess_db()

            assert result is mock_db_instance


class TestListUsersNoInprocess:
    """Tests for list_users_no_inprocess function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service.get_users_no_inprocess_db",
            lambda: mock_store,
        )

        result = list_users_no_inprocess()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestListActiveUsersNoInprocess:
    """Tests for list_active_users_no_inprocess function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns active records from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock()]
        mock_store.list_active.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service.get_users_no_inprocess_db",
            lambda: mock_store,
        )

        result = list_active_users_no_inprocess()

        assert result is mock_records
        mock_store.list_active.assert_called_once()


class TestGetUsersNoInprocess:
    """Tests for get_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service.get_users_no_inprocess_db",
            lambda: mock_store,
        )

        result = get_users_no_inprocess(123)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(123)


class TestGetUsersNoInprocessByUser:
    """Tests for get_users_no_inprocess_by_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_user."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_user.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service.get_users_no_inprocess_db",
            lambda: mock_store,
        )

        result = get_users_no_inprocess_by_user("TestUser")

        assert result is mock_record
        mock_store.fetch_by_user.assert_called_once_with("TestUser")


class TestAddUsersNoInprocess:
    """Tests for add_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service.get_users_no_inprocess_db",
            lambda: mock_store,
        )

        result = add_users_no_inprocess("TestUser", active=1)

        assert result is mock_record
        mock_store.add.assert_called_once_with("TestUser", 1)


class TestAddOrUpdateUsersNoInprocess:
    """Tests for add_or_update_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service.get_users_no_inprocess_db",
            lambda: mock_store,
        )

        result = add_or_update_users_no_inprocess("TestUser", active=0)

        assert result is mock_record
        mock_store.add_or_update.assert_called_once_with("TestUser", 0)


class TestUpdateUsersNoInprocess:
    """Tests for update_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service.get_users_no_inprocess_db",
            lambda: mock_store,
        )

        result = update_users_no_inprocess(1, active=0)

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, active=0)


class TestDeleteUsersNoInprocess:
    """Tests for delete_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service.get_users_no_inprocess_db",
            lambda: mock_store,
        )

        result = delete_users_no_inprocess(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)


class TestShouldHideFromInprocess:
    """Tests for should_hide_from_inprocess function."""

    def test_returns_true_when_record_exists_and_active(self, monkeypatch):
        """Test that function returns True when record exists and is active."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.active = 1
        mock_store.fetch_by_user.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service.get_users_no_inprocess_db",
            lambda: mock_store,
        )

        result = should_hide_from_inprocess("TestUser")

        assert result is True

    def test_returns_false_when_record_exists_but_inactive(self, monkeypatch):
        """Test that function returns False when record exists but is inactive."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.active = 0
        mock_store.fetch_by_user.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service.get_users_no_inprocess_db",
            lambda: mock_store,
        )

        result = should_hide_from_inprocess("TestUser")

        assert result is False

    def test_returns_false_when_no_record(self, monkeypatch):
        """Test that function returns False when no record found."""
        mock_store = MagicMock()
        mock_store.fetch_by_user.return_value = None
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.users_no_inprocess_service.get_users_no_inprocess_db",
            lambda: mock_store,
        )

        result = should_hide_from_inprocess("TestUser")

        assert result is False
