"""
Unit tests for domain/services/users_service.py module.

Tests for users service layer which provides cached access to UsersDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.users_service import (
    add_or_update_user,
    add_user,
    delete_user,
    get_user,
    get_user_by_username,
    get_users_db,
    list_users,
    list_users_by_group,
    update_user,
    user_exists,
)


class TestGetUsersDb:
    """Tests for get_users_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.services.users_service._USERS_STORE", mock_db)
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.has_db_config", lambda: True)

        result = get_users_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr("src.app_main.public.domain.services.users_service._USERS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="UsersDB requires database configuration"):
            get_users_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new UsersDB is created when none cached."""
        monkeypatch.setattr("src.app_main.public.domain.services.users_service._USERS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.users_service.UsersDB") as MockDB:
            MockDB.return_value = mock_db_instance

            result = get_users_db()

            assert result is mock_db_instance


class TestListUsers:
    """Tests for list_users function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.get_users_db", lambda: mock_store)

        result = list_users()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestListUsersByGroup:
    """Tests for list_users_by_group function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns filtered list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock()]
        mock_store.list_by_group.return_value = mock_records
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.get_users_db", lambda: mock_store)

        result = list_users_by_group("Translators")

        assert result is mock_records
        mock_store.list_by_group.assert_called_once_with("Translators")


class TestGetUser:
    """Tests for get_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.get_users_db", lambda: mock_store)

        result = get_user(123)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(123)


class TestGetUserByUsername:
    """Tests for get_user_by_username function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_username."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_username.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.get_users_db", lambda: mock_store)

        result = get_user_by_username("TestUser")

        assert result is mock_record
        mock_store.fetch_by_username.assert_called_once_with("TestUser")


class TestAddUser:
    """Tests for add_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.get_users_db", lambda: mock_store)

        result = add_user("TestUser", email="test@example.com", wiki="ar.wikipedia.org")

        assert result is mock_record
        mock_store.add.assert_called_once_with("TestUser", "test@example.com", "ar.wikipedia.org", "Uncategorized")


class TestAddOrUpdateUser:
    """Tests for add_or_update_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add_or_update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.get_users_db", lambda: mock_store)

        result = add_or_update_user("TestUser", user_group="Translators")

        assert result is mock_record
        mock_store.add_or_update.assert_called_once_with("TestUser", "", "", "Translators")


class TestUpdateUser:
    """Tests for update_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.get_users_db", lambda: mock_store)

        result = update_user(1, email="new@example.com")

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, email="new@example.com")


class TestDeleteUser:
    """Tests for delete_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.get_users_db", lambda: mock_store)

        result = delete_user(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)


class TestUserExists:
    """Tests for user_exists function."""

    def test_returns_true_when_user_exists(self, monkeypatch):
        """Test that function returns True when user found."""
        mock_store = MagicMock()
        mock_store.fetch_by_username.return_value = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.get_users_db", lambda: mock_store)

        result = user_exists("TestUser")

        assert result is True

    def test_returns_false_when_user_not_found(self, monkeypatch):
        """Test that function returns False when user not found."""
        mock_store = MagicMock()
        mock_store.fetch_by_username.return_value = None
        monkeypatch.setattr("src.app_main.public.domain.services.users_service.get_users_db", lambda: mock_store)

        result = user_exists("Missing")

        assert result is False
