"""
Unit tests for db/db_pages_users_to_main.py module.

Tests for PagesUsersToMainDB database operations.
"""

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.config import DbConfig
from src.app_main.public.domain.db.db_pages_users_to_main import (
    PagesUsersToMainDB,
    PagesUsersToMainRecord,
)


@pytest.fixture
def sample_record_row():
    """Fixture for a sample pages_users_to_main row from database."""
    return {
        "id": 1,
        "new_target": "TestPage",
        "new_user": "TestUser",
        "new_qid": "Q123",
    }


class TestPagesUsersToMainDB:
    """Tests for PagesUsersToMainDB class."""

    def test_list_returns_all_records(self, monkeypatch, db_config, sample_record_row):
        """Test that list returns all pages_users_to_main records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_record_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_pages_users_to_main.Database", lambda db_data: mock_db)

        db = PagesUsersToMainDB(db_config)
        result = db.list()

        assert len(result) == 1
        assert all(isinstance(r, PagesUsersToMainRecord) for r in result)
        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM pages_users_to_main ORDER BY id ASC")

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_pages_users_to_main.Database", lambda db_data: mock_db)

        db = PagesUsersToMainDB(db_config)
        result = db.fetch_by_id(999)

        assert result is None

    def test_add_inserts_record(self, monkeypatch, db_config, sample_record_row):
        """Test that add inserts a new record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_record_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_pages_users_to_main.Database", lambda db_data: mock_db)

        db = PagesUsersToMainDB(db_config)
        result = db.add(new_target="TestPage", new_user="TestUser", new_qid="Q123")

        assert result is not None
        mock_db.execute_query.assert_called()

    def test_add_raises_on_integrity_error(self, monkeypatch, db_config):
        """Test that add raises ValueError on integrity error."""
        mock_db = MagicMock()
        mock_db.execute_query.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")

        monkeypatch.setattr("src.app_main.public.domain.db.db_pages_users_to_main.Database", lambda db_data: mock_db)

        db = PagesUsersToMainDB(db_config)
        with pytest.raises(ValueError, match="Failed to add"):
            db.add("TestPage", "TestUser", "Q123")

    def test_update_raises_when_not_found(self, monkeypatch, db_config):
        """Test that update raises ValueError when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_pages_users_to_main.Database", lambda db_data: mock_db)

        db = PagesUsersToMainDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            db.update(999)

    def test_update_executes_update_query(self, monkeypatch, db_config, sample_record_row):
        """Test that update executes correct UPDATE query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_record_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_pages_users_to_main.Database", lambda db_data: mock_db)

        db = PagesUsersToMainDB(db_config)
        db.update(1, new_qid="Q456")

        call_args = mock_db.execute_query_safe.call_args
        assert "UPDATE pages_users_to_main SET" in call_args[0][0]
        assert "`new_qid` = %s" in call_args[0][0]

    def test_delete_returns_record(self, monkeypatch, db_config, sample_record_row):
        """Test that delete returns the deleted record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_record_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_pages_users_to_main.Database", lambda db_data: mock_db)

        db = PagesUsersToMainDB(db_config)
        result = db.delete(1)

        assert result.id == 1
        mock_db.execute_query_safe.assert_called_with("DELETE FROM pages_users_to_main WHERE id = %s", (1,))

    def test_delete_raises_when_not_found(self, monkeypatch, db_config):
        """Test that delete raises ValueError when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_pages_users_to_main.Database", lambda db_data: mock_db)

        db = PagesUsersToMainDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            db.delete(999)
