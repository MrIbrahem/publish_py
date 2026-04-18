"""
Unit tests for db.db_users_no_inprocess module.

Tests for UsersNoInprocess database operations.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.admin.domain.db.db_users_no_inprocess import UsersNoInprocessDB
from src.app_main.config import DbConfig
from src.db_models.admin_models import UsersNoInprocessRecord


class TestUsersNoInprocessDB:
    """Tests for UsersNoInprocessDB class."""

    def test_fetch_by_id_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns record when ID exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "user": "TestUser", "active": 1}]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_users_no_inprocess.Database", lambda db_data: mock_db)

        users_db = UsersNoInprocessDB(db_config)
        result = users_db.fetch_by_id(1)

        assert isinstance(result, UsersNoInprocessRecord)
        assert result.id == 1
        assert result.user == "TestUser"

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when ID not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.admin.domain.db.db_users_no_inprocess.Database", lambda db_data: mock_db)

        users_db = UsersNoInprocessDB(db_config)
        result = users_db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_user_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_user returns record when user exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "user": "HiddenUser", "active": 1}]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_users_no_inprocess.Database", lambda db_data: mock_db)

        users_db = UsersNoInprocessDB(db_config)
        result = users_db.fetch_by_user("HiddenUser")

        assert isinstance(result, UsersNoInprocessRecord)
        assert result.user == "HiddenUser"

    def test_list_returns_all_records(self, monkeypatch, db_config):
        """Test that list returns all users_no_inprocess records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "user": "User1", "active": 1},
            {"id": 2, "user": "User2", "active": 0},
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_users_no_inprocess.Database", lambda db_data: mock_db)

        users_db = UsersNoInprocessDB(db_config)
        result = users_db.list()

        assert len(result) == 2
        assert all(isinstance(r, UsersNoInprocessRecord) for r in result)

    def test_list_active_returns_only_active_records(self, monkeypatch, db_config):
        """Test that list_active returns only active records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "user": "ActiveUser", "active": 1},
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_users_no_inprocess.Database", lambda db_data: mock_db)

        users_db = UsersNoInprocessDB(db_config)
        result = users_db.list_active()

        assert len(result) == 1
        assert result[0].active == 1

    def test_add_inserts_new_record(self, monkeypatch, db_config):
        """Test that add inserts a new users_no_inprocess record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "user": "NewUser", "active": 1}]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_users_no_inprocess.Database", lambda db_data: mock_db)

        users_db = UsersNoInprocessDB(db_config)
        result = users_db.add("NewUser", 1)

        assert isinstance(result, UsersNoInprocessRecord)
        assert result.user == "NewUser"

    def test_add_raises_error_when_user_empty(self, monkeypatch, db_config):
        """Test that add raises ValueError when user is empty."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.admin.domain.db.db_users_no_inprocess.Database", lambda db_data: mock_db)

        users_db = UsersNoInprocessDB(db_config)
        with pytest.raises(ValueError, match="User is required"):
            users_db.add("")

    def test_update_modifies_record(self, monkeypatch, db_config):
        """Test that update modifies a users_no_inprocess record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.side_effect = [
            [{"id": 1, "user": "OldUser", "active": 1}],
            [{"id": 1, "user": "UpdatedUser", "active": 0}],
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_users_no_inprocess.Database", lambda db_data: mock_db)

        users_db = UsersNoInprocessDB(db_config)
        result = users_db.update(1, user="UpdatedUser", active=0)

        assert isinstance(result, UsersNoInprocessRecord)
        assert result.user == "UpdatedUser"

    def test_delete_removes_record(self, monkeypatch, db_config):
        """Test that delete removes a users_no_inprocess record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "user": "TestUser", "active": 1}]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_users_no_inprocess.Database", lambda db_data: mock_db)

        users_db = UsersNoInprocessDB(db_config)
        result = users_db.delete(1)

        assert isinstance(result, UsersNoInprocessRecord)

    def test_add_or_update_upserts_record(self, monkeypatch, db_config):
        """Test that add_or_update upserts a users_no_inprocess record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "user": "TestUser", "active": 1}]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_users_no_inprocess.Database", lambda db_data: mock_db)

        users_db = UsersNoInprocessDB(db_config)
        result = users_db.add_or_update("TestUser", 1)

        assert isinstance(result, UsersNoInprocessRecord)
        assert result.user == "TestUser"
