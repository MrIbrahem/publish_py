from unittest.mock import MagicMock, patch

import pytest

from src.main_app.db.exceptions import DuplicateUserError
from src.main_app.db.models import AdminUserRecord
from src.main_app.db.services.users.admin_service import (
    active_coordinators,
    add_coordinator,
    delete_coordinator,
    get_coordinator_by_id,
    is_active_coordinator,
    list_coordinators,
    set_coordinator_active,
)


def test_coordinator_workflow():
    # Test add
    c = add_coordinator("Wiki_User")
    assert c.username == "Wiki_User"
    assert c.is_active == 1
    assert c.id is not None

    # Test get
    c2 = get_coordinator_by_id(c.id)
    assert c2.username == "Wiki_User"

    # Test list
    all_c = list_coordinators()
    assert len(all_c) >= 1
    assert any(x.username == "Wiki_User" for x in all_c)

    # Test active
    active = active_coordinators()
    assert "Wiki_User" in active

    # Test update
    updated = set_coordinator_active(c.id, False)
    assert updated.is_active == 0

    assert "Wiki_User" not in active_coordinators()

    # Test is_active_coordinator
    assert is_active_coordinator("Wiki_User") is False
    set_coordinator_active(c.id, True)
    assert is_active_coordinator("Wiki_User") is True

    # Test delete
    deleted = delete_coordinator(c.id)
    assert deleted is True
    assert get_coordinator_by_id(c.id) is None


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
        add_coordinator("Active_Editor")
        active = active_coordinators()
        assert "Active_Editor" in active


class TestGetCoordinator:
    """Tests for get_coordinator_by_id function."""

    def test_returns_coordinator_record(self, monkeypatch):
        """Test that function returns a AdminUserRecord."""
        c = add_coordinator("Medic_Expert")
        result = get_coordinator_by_id(c.id)
        assert isinstance(result, AdminUserRecord)
        assert result.username == "Medic_Expert"

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when coordinator not found."""
        assert get_coordinator_by_id(8888) is None


class TestAddCoordinator:
    """Tests for add_coordinator function."""

    def test_adds_coordinator_and_returns_record(self, monkeypatch):
        """Test that add_coordinator adds and returns the record."""
        record = add_coordinator("New_Admin")
        assert record.username == "New_Admin"

    def test_raises_error_if_exists(self, monkeypatch):
        add_coordinator("Duplicate")
        with pytest.raises(DuplicateUserError, match="Coordinator 'Duplicate' already exists"):
            add_coordinator("Duplicate")

    def test_raises_error_if_no_username(self, monkeypatch):
        with pytest.raises(ValueError, match="Username is required"):
            add_coordinator("")


class TestDeleteCoordinator:
    """Tests for delete_coordinator function."""

    def test_deletes_coordinator(self, monkeypatch):
        """Test that delete_coordinator calls store delete."""
        c = add_coordinator("Delete_Me")
        deleted = delete_coordinator(c.id)
        assert deleted is True
        assert get_coordinator_by_id(c.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert delete_coordinator(9999) is False


class TestIsCoordinator:
    """Tests for is_active_coordinator function."""

    def test_returns_true_when_user_is_active_coordinator(self, monkeypatch):
        """Test that is_active_coordinator returns True for active coordinator."""
        add_coordinator("Active_Coord")
        assert is_active_coordinator("Active_Coord") is True

    def test_returns_false_when_user_not_coordinator(self, monkeypatch):
        """Test that is_active_coordinator returns False when username not found."""
        assert is_active_coordinator("Random_User") is False
