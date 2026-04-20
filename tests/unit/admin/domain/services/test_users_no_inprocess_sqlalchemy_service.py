from unittest.mock import MagicMock, patch

import pytest
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
from src.sqlalchemy_app.admin.domain_models import UsersNoInprocessRecord


def test_users_no_inprocess_workflow():
    # Test add
    rec = add_users_no_inprocess("User_1", 1)
    assert rec.user == "User_1"
    assert rec.active == 1

    # Test get
    rec2 = get_users_no_inprocess(rec.id)
    assert rec2.user == "User_1"

    # Test get by user
    rec3 = get_users_no_inprocess_by_user("User_1")
    assert rec3.id == rec.id

    # Test list
    all_rec = list_users_no_inprocess()
    assert any(x.user == "User_1" for x in all_rec)

    # Test active
    active = list_active_users_no_inprocess()
    assert any(x.user == "User_1" for x in active)

    # Test update
    updated = update_users_no_inprocess(rec.id, active=0)
    assert updated.active == 0
    assert should_hide_from_inprocess("User_1") is False

    # Test add_or_update
    rec4 = add_or_update_users_no_inprocess("User_1", 1)
    assert rec4.active == 1
    assert should_hide_from_inprocess("User_1") is True

    # Test delete
    delete_users_no_inprocess(rec.id)
    assert get_users_no_inprocess(rec.id) is None


class TestListUsersNoInprocess:
    """Tests for list_users_no_inprocess function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns all records."""
        add_users_no_inprocess("User_One")
        add_users_no_inprocess("User_Two")
        result = list_users_no_inprocess()
        assert len(result) >= 2


class TestListActiveUsersNoInprocess:
    """Tests for list_active_users_no_inprocess function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns active records."""
        add_users_no_inprocess("Active_Wiki_User", active=1)
        add_users_no_inprocess("Inactive_Wiki_User", active=0)
        active = list_active_users_no_inprocess()
        assert len(active) == 1
        assert active[0].user == "Active_Wiki_User"


class TestGetUsersNoInprocess:
    """Tests for get_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        rec = add_users_no_inprocess("Clinical_Editor")
        result = get_users_no_inprocess(rec.id)
        assert isinstance(result, UsersNoInprocessRecord)
        assert result.user == "Clinical_Editor"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_users_no_inprocess(9999) is None


class TestGetUsersNoInprocessByUser:
    """Tests for get_users_no_inprocess_by_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by username."""
        add_users_no_inprocess("Medical_Librarian")
        result = get_users_no_inprocess_by_user("Medical_Librarian")
        assert result.user == "Medical_Librarian"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_users_no_inprocess_by_user("Ghost") is None


class TestAddUsersNoInprocess:
    """Tests for add_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns the record."""
        record = add_users_no_inprocess("Science_Writer")
        assert record.user == "Science_Writer"

    def test_raises_error_if_exists(self, monkeypatch):
        add_users_no_inprocess("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            add_users_no_inprocess("Duplicate")

    def test_raises_error_if_no_user(self, monkeypatch):
        with pytest.raises(ValueError, match="User is required"):
            add_users_no_inprocess("")


class TestAddOrUpdateUsersNoInprocess:
    """Tests for add_or_update_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts the record."""
        add_users_no_inprocess("Regular_Editor", active=1)
        record = add_or_update_users_no_inprocess("Regular_Editor", active=0)
        assert record.active == 0
        assert len(list_users_no_inprocess()) == 1

    def test_raises_error_if_no_user(self, monkeypatch):
        with pytest.raises(ValueError, match="User is required"):
            add_or_update_users_no_inprocess(" ")


class TestUpdateUsersNoInprocess:
    """Tests for update_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns the record."""
        rec = add_users_no_inprocess("Target_User", active=1)
        updated = update_users_no_inprocess(rec.id, active=0)
        assert updated.active == 0

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        rec = add_users_no_inprocess("No_Change")
        result = update_users_no_inprocess(rec.id)
        assert result.user == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_users_no_inprocess(9999, active=0)


class TestDeleteUsersNoInprocess:
    """Tests for delete_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        rec = add_users_no_inprocess("To_Delete")
        delete_users_no_inprocess(rec.id)
        assert get_users_no_inprocess(rec.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_users_no_inprocess(9999)


class TestShouldHideFromInprocess:
    """Tests for should_hide_from_inprocess function."""

    def test_returns_true_when_record_exists_and_active(self, monkeypatch):
        """Test that function returns True when record exists and is active."""
        add_users_no_inprocess("Quiet_Editor", active=1)
        assert should_hide_from_inprocess("Quiet_Editor") is True

    def test_returns_false_when_record_exists_but_inactive(self, monkeypatch):
        """Test that function returns False when record exists but is inactive."""
        add_users_no_inprocess("Noisy_Editor", active=0)
        assert should_hide_from_inprocess("Noisy_Editor") is False

    def test_returns_false_when_no_record(self, monkeypatch):
        """Test that function returns False when no record found."""
        assert should_hide_from_inprocess("Ghost_Account") is False
