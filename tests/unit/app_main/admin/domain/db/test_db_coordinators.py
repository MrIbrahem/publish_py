"""
Unit tests for db.db_coordinators module.

Tests for Coordinators database operations.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.admin.domain.db.db_coordinators import CoordinatorsDB
from src.app_main.config import DbConfig
from src.db_models.admin_models import CoordinatorRecord


class TestCoordinatorsDB:
    """Tests for CoordinatorsDB class."""

    def test_fetch_by_id_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns record when ID exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "username": "TestUser", "is_active": 1}]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        result = coordinators_db.fetch_by_id(1)

        assert isinstance(result, CoordinatorRecord)
        assert result.id == 1
        assert result.username == "TestUser"
        assert result.is_active == 1

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when ID not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        result = coordinators_db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_user_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_user returns record when username exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "username": "TestUser", "is_active": 1}]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        result = coordinators_db.fetch_by_user("TestUser")

        assert isinstance(result, CoordinatorRecord)
        assert result.username == "TestUser"

    def test_fetch_by_user_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_user returns None when username not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        result = coordinators_db.fetch_by_user("NonExistent")

        assert result is None

    def test_list_returns_all_records(self, monkeypatch, db_config):
        """Test that list returns all coordinator records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "username": "User1", "is_active": 1},
            {"id": 2, "username": "User2", "is_active": 0},
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        result = coordinators_db.list()

        assert len(result) == 2
        assert all(isinstance(r, CoordinatorRecord) for r in result)

    def test_list_active_returns_only_active_records(self, monkeypatch, db_config):
        """Test that list_active returns only is_active records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "username": "User1", "is_active": 1},
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        result = coordinators_db.list_active()

        assert len(result) == 1
        assert result[0].is_active == 1

    def test_add_inserts_new_record(self, monkeypatch, db_config):
        """Test that add inserts a new coordinator record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "username": "NewUser", "is_active": 1}]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        result = coordinators_db.add("NewUser", 1)

        mock_db.execute_query.assert_called_once()
        assert isinstance(result, CoordinatorRecord)
        assert result.username == "NewUser"

    def test_add_raises_error_when_user_empty(self, monkeypatch, db_config):
        """Test that add raises ValueError when username is empty."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        with pytest.raises(ValueError, match="User is required"):
            coordinators_db.add("")

    def test_add_raises_error_on_duplicate(self, monkeypatch, db_config):
        """Test that add raises ValueError on duplicate username."""
        mock_db = MagicMock()
        mock_db.execute_query.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        with pytest.raises(ValueError, match="Coordinator 'TestUser' already exists"):
            coordinators_db.add("TestUser")

    def test_update_modifies_record(self, monkeypatch, db_config):
        """Test that update modifies a coordinator record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.side_effect = [
            [{"id": 1, "username": "OldUser", "is_active": 1}],
            [{"id": 1, "username": "UpdatedUser", "is_active": 0}],
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        result = coordinators_db.update(1, username="UpdatedUser", is_active=0)

        assert isinstance(result, CoordinatorRecord)
        assert result.username == "UpdatedUser"
        assert result.is_active == 0

    def test_update_raises_error_when_record_not_found(self, monkeypatch, db_config):
        """Test that update raises ValueError when record not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        with pytest.raises(ValueError, match="Coordinator record with ID 999 not found"):
            coordinators_db.update(999, username="NewUser")

    def test_delete_removes_record(self, monkeypatch, db_config):
        """Test that delete removes a coordinator record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "username": "TestUser", "is_active": 1}]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        coordinators_db.delete(1)

        mock_db.execute_query_safe.assert_called_with(
            "DELETE FROM coordinators WHERE id = %s",
            (1,),
        )

    def test_delete_raises_error_when_record_not_found(self, monkeypatch, db_config):
        """Test that delete raises ValueError when record not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        with pytest.raises(ValueError, match="Coordinator record with ID 999 not found"):
            coordinators_db.delete(999)

    def test_add_or_update_upserts_record(self, monkeypatch, db_config):
        """Test that add_or_update upserts a coordinator record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "username": "TestUser", "is_active": 1}]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_coordinators.Database", lambda db_data: mock_db)

        coordinators_db = CoordinatorsDB(db_config)
        result = coordinators_db.add_or_update("TestUser", 1)

        assert isinstance(result, CoordinatorRecord)
        assert result.username == "TestUser"
