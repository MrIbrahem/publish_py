from unittest.mock import MagicMock, patch

import pytest
from src.db_models.admin_models import UsersNoInprocessRecord
from src.sqlalchemy_app.admin.domain.models import _UsersNoInprocessRecord
from src.sqlalchemy_app.admin.domain.services.users_no_inprocess_service import (
    add_or_update_users_no_inprocess,
    add_users_no_inprocess,
    delete_users_no_inprocess,
    get_users_no_inprocess,
    get_users_no_inprocess_by_user,
    list_active_users_no_inprocess,
    list_users_no_inprocess,
    should_hide_from_inprocess,
    update_users_no_inprocess,
)


def test_users_no_inprocess_workflow():
    # Test add
    rec = add_users_no_inprocess("test_user", 1)
    assert rec.user == "test_user"
    assert rec.active == 1

    # Test get
    rec2 = get_users_no_inprocess(rec.id)
    assert rec2.user == "test_user"

    # Test get by user
    rec3 = get_users_no_inprocess_by_user("test_user")
    assert rec3.id == rec.id

    # Test list
    all_rec = list_users_no_inprocess()
    assert any(x.user == "test_user" for x in all_rec)

    # Test active
    active = list_active_users_no_inprocess()
    assert any(x.user == "test_user" for x in active)

    # Test update
    updated = update_users_no_inprocess(rec.id, active=0)
    assert updated.active == 0
    assert should_hide_from_inprocess("test_user") is False

    # Test add_or_update
    rec4 = add_or_update_users_no_inprocess("test_user", 1)
    assert rec4.active == 1
    assert should_hide_from_inprocess("test_user") is True

    # Test delete
    delete_users_no_inprocess(rec.id)
    assert get_users_no_inprocess(rec.id) is None


class TestGetUsersNoInprocessDb:
    """Tests for get_users_no_inprocess_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new UsersNoInprocessDB is created when none cached."""


class TestListUsersNoInprocess:
    """Tests for list_users_no_inprocess function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""


class TestListActiveUsersNoInprocess:
    """Tests for list_active_users_no_inprocess function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns active records from store."""


class TestGetUsersNoInprocess:
    """Tests for get_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""


class TestGetUsersNoInprocessByUser:
    """Tests for get_users_no_inprocess_by_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_user."""


class TestAddUsersNoInprocess:
    """Tests for add_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""


class TestAddOrUpdateUsersNoInprocess:
    """Tests for add_or_update_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""


class TestUpdateUsersNoInprocess:
    """Tests for update_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""


class TestDeleteUsersNoInprocess:
    """Tests for delete_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""


class TestShouldHideFromInprocess:
    """Tests for should_hide_from_inprocess function."""

    def test_returns_true_when_record_exists_and_active(self, monkeypatch):
        """Test that function returns True when record exists and is active."""

    def test_returns_false_when_record_exists_but_inactive(self, monkeypatch):
        """Test that function returns False when record exists but is inactive."""

    def test_returns_false_when_no_record(self, monkeypatch):
        """Test that function returns False when no record found."""
