"""
Unit tests for db/db_users.py module.

Tests for UsersDB database operations.
"""

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.config import DbConfig
from src.app_main.public.domain.db.db_users import (
    UserRecord,
    UsersDB,
)


@pytest.fixture
def sample_user_row():
    """Fixture for a sample user row from database."""
    return {
        "user_id": 1,
        "username": "TestUser",
        "email": "test@example.com",
        "wiki": "ar.wikipedia.org",
        "user_group": "Translators",
    }


class TestUsersDB:
    """Tests for UsersDB class."""

    def test_list_returns_all_records(self, monkeypatch, db_config, sample_user_row):
        """Test that list returns all user records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_user_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_users.Database", lambda db_data: mock_db)

        db = UsersDB(db_config)
        result = db.list()

        assert len(result) == 1
        assert all(isinstance(r, UserRecord) for r in result)
        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM users ORDER BY user_id ASC")

    def test_list_by_group(self, monkeypatch, db_config, sample_user_row):
        """Test that list_by_group returns filtered records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_user_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_users.Database", lambda db_data: mock_db)

        db = UsersDB(db_config)
        result = db.list_by_group("Translators")

        assert len(result) == 1
        mock_db.fetch_query_safe.assert_called_with(
            "SELECT * FROM users WHERE user_group = %s ORDER BY user_id ASC",
            ("Translators",),
        )

    def test_add_requires_non_empty_username(self, monkeypatch, db_config):
        """Test that add requires non-empty username."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_users.Database", lambda db_data: mock_db)

        db = UsersDB(db_config)
        with pytest.raises(ValueError, match="Username is required"):
            db.add("")

    def test_add_strips_whitespace(self, monkeypatch, db_config):
        """Test that add strips whitespace from username."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"user_id": 1, "username": "TestUser"}]

        monkeypatch.setattr("src.app_main.public.domain.db.db_users.Database", lambda db_data: mock_db)

        db = UsersDB(db_config)
        db.add("  TestUser  ")

        call_args = mock_db.execute_query.call_args
        assert "TestUser" in call_args[0][1]

    def test_add_raises_on_duplicate(self, monkeypatch, db_config):
        """Test that add raises ValueError on duplicate."""
        mock_db = MagicMock()
        mock_db.execute_query.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")

        monkeypatch.setattr("src.app_main.public.domain.db.db_users.Database", lambda db_data: mock_db)

        db = UsersDB(db_config)
        with pytest.raises(ValueError, match="already exists"):
            db.add("TestUser")

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_users.Database", lambda db_data: mock_db)

        db = UsersDB(db_config)
        result = db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_username_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_username returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_users.Database", lambda db_data: mock_db)

        db = UsersDB(db_config)
        result = db.fetch_by_username("Missing")

        assert result is None

    def test_update_raises_when_not_found(self, monkeypatch, db_config):
        """Test that update raises ValueError when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_users.Database", lambda db_data: mock_db)

        db = UsersDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            db.update(999)

    def test_delete_returns_record(self, monkeypatch, db_config, sample_user_row):
        """Test that delete returns the deleted record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_user_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_users.Database", lambda db_data: mock_db)

        db = UsersDB(db_config)
        result = db.delete(1)

        assert result.user_id == 1
        mock_db.execute_query_safe.assert_called_with("DELETE FROM users WHERE user_id = %s", (1,))

    def test_add_or_update_executes_upsert(self, monkeypatch, db_config, sample_user_row):
        """Test that add_or_update executes correct upsert query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_user_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_users.Database", lambda db_data: mock_db)

        db = UsersDB(db_config)
        db.add_or_update("TestUser", email="new@example.com")

        call_args = mock_db.execute_query_safe.call_args
        assert "INSERT INTO users" in call_args[0][0]
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]
