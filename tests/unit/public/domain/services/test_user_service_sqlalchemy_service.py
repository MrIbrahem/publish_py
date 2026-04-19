"""
TODO: write tests
"""

from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import UserRecord
from src.sqlalchemy_app.public.domain.models import _UserRecord
from src.sqlalchemy_app.public.domain.services.user_service import (
    add_or_update_user,
    add_user,
    delete_user,
    get_user,
    get_user_by_username,
    list_users,
    list_users_by_group,
    update_user,
    user_exists,
)
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db





def test_user_workflow():
    u = add_user("test_user", "test@example.com", "enwiki", "Editor")
    assert u.username == "test_user"
    assert get_user(u.user_id).username == "test_user"
    assert get_user_by_username("test_user").user_id == u.user_id
    assert any(x.username == "test_user" for x in list_users())
    assert any(x.username == "test_user" for x in list_users_by_group("Editor"))
    updated = update_user(u.user_id, email="new@example.com")
    assert updated.email == "new@example.com"
    assert user_exists("test_user") is True
    u4 = add_or_update_user("test_user", email="final@example.com")
    assert u4.email == "final@example.com"
    delete_user(u.user_id)
    assert get_user(u.user_id) is None

class TestGetUsersDb:
    """Tests for get_users_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new UsersDB is created when none cached."""


class TestListUsers:
    """Tests for list_users function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""


class TestListUsersByGroup:
    """Tests for list_users_by_group function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns filtered list from store."""


class TestGetUser:
    """Tests for get_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""


class TestGetUserByUsername:
    """Tests for get_user_by_username function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_username."""


class TestAddUser:
    """Tests for add_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""


class TestAddOrUpdateUser:
    """Tests for add_or_update_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add_or_update."""


class TestUpdateUser:
    """Tests for update_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""


class TestDeleteUser:
    """Tests for delete_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""


class TestUserExists:
    """Tests for user_exists function."""

    def test_returns_true_when_user_exists(self, monkeypatch):
        """Test that function returns True when user found."""

    def test_returns_false_when_user_not_found(self, monkeypatch):
        """Test that function returns False when user not found."""
