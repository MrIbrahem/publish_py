"""
Unit tests for coordinators_service module.
"""

from unittest.mock import MagicMock

import pytest
from src.app_main.admin.domain.services.coordinators_service import (
    active_coordinators,
    add_coordinator,
    add_or_update_coordinator,
    delete_coordinator,
    get_coordinator,
    get_coordinator_by_user,
    get_coordinators_db,
    is_coordinator,
    list_coordinators,
    update_coordinator,
)


class TestGetCoordinatorsDb:
    """Tests for get_coordinators_db function."""

    def test_returns_cached_instance_on_subsequent_calls(self, monkeypatch):
        """Test that the same instance is returned on multiple calls."""
        mock_store = MagicMock()
        monkeypatch.setattr("src.app_main.admin.domain.services.coordinators_service._COORDINATORS_STORE", mock_store)

        result1 = get_coordinators_db()
        result2 = get_coordinators_db()

        assert result1 is result2
        assert result1 is mock_store

    def test_raises_error_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when database config is missing."""
        monkeypatch.setattr("src.app_main.admin.domain.services.coordinators_service.has_db_config", lambda: False)
        monkeypatch.setattr("src.app_main.admin.domain.services.coordinators_service._COORDINATORS_STORE", None)

        with pytest.raises(RuntimeError, match="CoordinatorsDB requires database configuration"):
            get_coordinators_db()


class TestListCoordinators:
    """Tests for list_coordinators function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_coordinators returns all records."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.coordinators_service.get_coordinators_db", lambda: mock_store
        )

        result = list_coordinators()

        assert result == mock_records
        mock_store.list.assert_called_once()


class TestListActiveCoordinators:
    """Tests for active_coordinators function."""

    def test_returns_active_records(self, monkeypatch):
        """Test that active_coordinators returns active records."""
        mock_store = MagicMock()
        mock_records = [MagicMock()]
        mock_store.list_active.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.coordinators_service.get_coordinators_db", lambda: mock_store
        )

        result = active_coordinators()

        assert result == mock_records
        mock_store.list_active.assert_called_once()


class TestGetCoordinator:
    """Tests for get_coordinator function."""

    def test_returns_coordinator_record(self, monkeypatch):
        """Test that function returns a CoordinatorRecord."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.coordinators_service.get_coordinators_db", lambda: mock_store
        )

        result = get_coordinator(1)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(1)

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when coordinator not found."""
        mock_store = MagicMock()
        mock_store.fetch_by_id.return_value = None
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.coordinators_service.get_coordinators_db", lambda: mock_store
        )

        result = get_coordinator(999)

        assert result is None


class TestGetCoordinatorByUser:
    """Tests for get_coordinator_by_user function."""

    def test_returns_coordinator_by_user(self, monkeypatch):
        """Test that function returns coordinator by username."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_user.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.coordinators_service.get_coordinators_db", lambda: mock_store
        )

        result = get_coordinator_by_user("TestUser")

        assert result is mock_record
        mock_store.fetch_by_user.assert_called_once_with("TestUser")


class TestAddCoordinator:
    """Tests for add_coordinator function."""

    def test_adds_coordinator_and_returns_record(self, monkeypatch):
        """Test that add_coordinator adds and returns the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.coordinators_service.get_coordinators_db", lambda: mock_store
        )

        result = add_coordinator("NewUser", 1)

        mock_store.add.assert_called_once_with("NewUser", 1)
        assert result is mock_record


class TestAddOrUpdateCoordinator:
    """Tests for add_or_update_coordinator function."""

    def test_upserts_coordinator(self, monkeypatch):
        """Test that add_or_update_coordinator upserts the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.coordinators_service.get_coordinators_db", lambda: mock_store
        )

        result = add_or_update_coordinator("TestUser", 1)

        mock_store.add_or_update.assert_called_once_with("TestUser", 1)
        assert result is mock_record


class TestUpdateCoordinator:
    """Tests for update_coordinator function."""

    def test_updates_coordinator_and_returns_record(self, monkeypatch):
        """Test that update_coordinator updates and returns the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.coordinators_service.get_coordinators_db", lambda: mock_store
        )

        result = update_coordinator(1, user="UpdatedUser", active=0)

        mock_store.update.assert_called_once_with(1, user="UpdatedUser", active=0)
        assert result is mock_record


class TestDeleteCoordinator:
    """Tests for delete_coordinator function."""

    def test_deletes_coordinator(self, monkeypatch):
        """Test that delete_coordinator calls store delete."""
        mock_store = MagicMock()
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.coordinators_service.get_coordinators_db", lambda: mock_store
        )

        delete_coordinator(1)

        mock_store.delete.assert_called_once_with(1)


class TestIsCoordinator:
    """Tests for is_coordinator function."""

    def test_returns_true_when_user_is_active_coordinator(self, monkeypatch):
        """Test that is_coordinator returns True for active coordinator."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.active = 1
        mock_store.fetch_by_user.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.coordinators_service.get_coordinators_db", lambda: mock_store
        )

        result = is_coordinator("CoordinatorUser")

        assert result is True

    def test_returns_false_when_user_not_coordinator(self, monkeypatch):
        """Test that is_coordinator returns False when user not found."""
        mock_store = MagicMock()
        mock_store.fetch_by_user.return_value = None
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.coordinators_service.get_coordinators_db", lambda: mock_store
        )

        result = is_coordinator("RegularUser")

        assert result is False

    def test_returns_false_when_coordinator_inactive(self, monkeypatch):
        """Test that is_coordinator returns False for inactive coordinator."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.active = 0
        mock_store.fetch_by_user.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.coordinators_service.get_coordinators_db", lambda: mock_store
        )

        result = is_coordinator("InactiveCoordinator")

        assert result is False
