from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.shared.engine import init_db
from src.sqlalchemy_app.shared.services.coordinator_service import (
    active_coordinators,
    add_coordinator,
    add_or_update_coordinator,
    delete_coordinator,
    get_coordinator,
    get_coordinator_by_user,
    is_coordinator,
    list_coordinators,
    set_coordinator_active,
    update_coordinator,
)
from src.sqlalchemy_app.sqlalchemy_models import CoordinatorRecord


def test_coordinator_workflow():
    # Test add
    c = add_coordinator("Wiki_User", 1)
    assert c.username == "Wiki_User"
    assert c.is_active == 1
    assert c.id is not None

    # Test get
    c2 = get_coordinator(c.id)
    assert c2.username == "Wiki_User"

    # Test get by user
    c3 = get_coordinator_by_user("Wiki_User")
    assert c3.id == c.id

    # Test list
    all_c = list_coordinators()
    assert len(all_c) >= 1
    assert any(x.username == "Wiki_User" for x in all_c)

    # Test active
    active_coordinators.cache_clear()
    active = active_coordinators()
    assert "Wiki_User" in active

    # Test update
    updated = update_coordinator(c.id, is_active=0)
    assert updated.is_active == 0

    active_coordinators.cache_clear()
    assert "Wiki_User" not in active_coordinators()

    # Test is_coordinator
    assert is_coordinator("Wiki_User") is False
    set_coordinator_active(c.id, True)
    assert is_coordinator("Wiki_User") is True

    # Test add_or_update
    c4 = add_or_update_coordinator("Wiki_User", 0)
    assert c4.is_active == 0

    # Test delete
    delete_coordinator(c.id)
    assert get_coordinator(c.id) is None


class TestListCoordinators:
    """Tests for list_coordinators function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_coordinators returns all records."""
        add_coordinator("User_Alpha")
        add_coordinator("User_Beta")
        result = list_coordinators()
        assert len(result) >= 2


class TestListActiveCoordinators:
    """Tests for active_coordinators function."""

    def test_returns_active_usernames(self, monkeypatch):
        """Test that active_coordinators returns active coordinator usernames."""
        active_coordinators.cache_clear()
        add_coordinator("Active_Editor", is_active=1)
        add_coordinator("Inactive_Editor", is_active=0)
        active = active_coordinators()
        assert "Active_Editor" in active
        assert "Inactive_Editor" not in active


class TestGetCoordinator:
    """Tests for get_coordinator function."""

    def test_returns_coordinator_record(self, monkeypatch):
        """Test that function returns a CoordinatorRecord."""
        c = add_coordinator("Medic_Expert")
        result = get_coordinator(c.id)
        assert isinstance(result, CoordinatorRecord)
        assert result.username == "Medic_Expert"

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when coordinator not found."""
        assert get_coordinator(8888) is None


class TestGetCoordinatorByUser:
    """Tests for get_coordinator_by_user function."""

    def test_returns_coordinator_by_user(self, monkeypatch):
        """Test that function returns coordinator by username."""
        add_coordinator("Wiki_Lead")
        result = get_coordinator_by_user("Wiki_Lead")
        assert result.username == "Wiki_Lead"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_coordinator_by_user("Ghost") is None


class TestAddCoordinator:
    """Tests for add_coordinator function."""

    def test_adds_coordinator_and_returns_record(self, monkeypatch):
        """Test that add_coordinator adds and returns the record."""
        record = add_coordinator("New_Admin")
        assert record.username == "New_Admin"

    def test_raises_error_if_exists(self, monkeypatch):
        add_coordinator("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            add_coordinator("Duplicate")

    def test_raises_error_if_no_username(self, monkeypatch):
        with pytest.raises(ValueError, match="username is required"):
            add_coordinator("")


class TestAddOrUpdateCoordinator:
    """Tests for add_or_update_coordinator function."""

    def test_upserts_coordinator(self, monkeypatch):
        """Test that add_or_update_coordinator upserts the record."""
        add_coordinator("Sync_User", is_active=1)
        record = add_or_update_coordinator("Sync_User", is_active=0)
        assert record.is_active == 0
        assert len(list_coordinators()) == 1

    def test_raises_error_if_no_username(self, monkeypatch):
        with pytest.raises(ValueError, match="username is required"):
            add_or_update_coordinator(" ")


class TestUpdateCoordinator:
    """Tests for update_coordinator function."""

    def test_updates_coordinator_and_returns_record(self, monkeypatch):
        """Test that update_coordinator updates and returns the record."""
        c = add_coordinator("Update_Me", is_active=1)
        updated = update_coordinator(c.id, is_active=0)
        assert updated.is_active == 0

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        c = add_coordinator("No_Change")
        result = update_coordinator(c.id)
        assert result.username == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_coordinator(9999, is_active=0)


class TestDeleteCoordinator:
    """Tests for delete_coordinator function."""

    def test_deletes_coordinator(self, monkeypatch):
        """Test that delete_coordinator calls store delete."""
        c = add_coordinator("Delete_Me")
        delete_coordinator(c.id)
        assert get_coordinator(c.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_coordinator(9999)


class TestIsCoordinator:
    """Tests for is_coordinator function."""

    def test_returns_true_when_user_is_active_coordinator(self, monkeypatch):
        """Test that is_coordinator returns True for active coordinator."""
        add_coordinator("Active_Coord", is_active=1)
        assert is_coordinator("Active_Coord") is True

    def test_returns_false_when_user_not_coordinator(self, monkeypatch):
        """Test that is_coordinator returns False when username not found."""
        assert is_coordinator("Random_User") is False

    def test_returns_false_when_coordinator_inactive(self, monkeypatch):
        """Test that is_coordinator returns False for inactive coordinator."""
        add_coordinator("Inactive_Coord", is_active=0)
        assert is_coordinator("Inactive_Coord") is False
