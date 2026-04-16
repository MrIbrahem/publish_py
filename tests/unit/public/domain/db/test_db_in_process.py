"""
Unit tests for db/db_in_process.py module.

Tests for InProcessDB database operations.
"""

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.config import DbConfig
from src.app_main.public.domain.db.db_in_process import (
    InProcessDB,
    InProcessRecord,
)





@pytest.fixture
def sample_in_process_row():
    """Fixture for a sample in_process row from database."""
    return {
        "id": 1,
        "title": "TestPage",
        "user": "TestUser",
        "lang": "ar",
        "cat": "RTT",
        "translate_type": "lead",
        "word": 100,
    }


class TestInProcessDB:
    """Tests for InProcessDB class."""

    def test_list_returns_all_records(self, monkeypatch, db_config, sample_in_process_row):
        """Test that list returns all in_process records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_in_process_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        result = db.list()

        assert len(result) == 1
        assert all(isinstance(r, InProcessRecord) for r in result)
        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM in_process ORDER BY id ASC")

    def test_list_by_user(self, monkeypatch, db_config, sample_in_process_row):
        """Test that list_by_user returns filtered records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_in_process_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        result = db.list_by_user("TestUser")

        assert len(result) == 1
        mock_db.fetch_query_safe.assert_called_with(
            "SELECT * FROM in_process WHERE user = %s ORDER BY id ASC",
            ("TestUser",),
        )

    def test_list_by_lang(self, monkeypatch, db_config, sample_in_process_row):
        """Test that list_by_lang returns filtered records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_in_process_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        result = db.list_by_lang("ar")

        assert len(result) == 1
        mock_db.fetch_query_safe.assert_called_with(
            "SELECT * FROM in_process WHERE lang = %s ORDER BY id ASC",
            ("ar",),
        )

    def test_add_requires_non_empty_title(self, monkeypatch, db_config):
        """Test that add requires non-empty title."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        with pytest.raises(ValueError, match="Title is required"):
            db.add("", "TestUser", "ar")

    def test_add_requires_non_empty_user(self, monkeypatch, db_config):
        """Test that add requires non-empty user."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        with pytest.raises(ValueError, match="User is required"):
            db.add("TestPage", "", "ar")

    def test_add_requires_non_empty_lang(self, monkeypatch, db_config):
        """Test that add requires non-empty lang."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        with pytest.raises(ValueError, match="Language is required"):
            db.add("TestPage", "TestUser", "")

    def test_add_strips_whitespace(self, monkeypatch, db_config):
        """Test that add strips whitespace from inputs."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "title": "Test", "user": "User", "lang": "ar"}]

        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        db.add("  Test  ", "  User  ", "  ar  ")

        call_args = mock_db.execute_query.call_args
        params = call_args[0][1]
        assert "Test" in params
        assert "User" in params
        assert "ar" in params

    def test_add_raises_on_duplicate(self, monkeypatch, db_config):
        """Test that add raises ValueError on duplicate."""
        mock_db = MagicMock()
        mock_db.execute_query.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")

        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        with pytest.raises(ValueError, match="already exists"):
            db.add("TestPage", "TestUser", "ar")

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        result = db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_title_user_lang_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_title_user_lang returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        result = db.fetch_by_title_user_lang("Missing", "User", "ar")

        assert result is None

    def test_update_raises_when_not_found(self, monkeypatch, db_config):
        """Test that update raises ValueError when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            db.update(999)

    def test_delete_returns_record(self, monkeypatch, db_config, sample_in_process_row):
        """Test that delete returns the deleted record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_in_process_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        result = db.delete(1)

        assert result.id == 1
        mock_db.execute_query_safe.assert_called_with("DELETE FROM in_process WHERE id = %s", (1,))

    def test_delete_by_title_user_lang(self, monkeypatch, db_config):
        """Test that delete_by_title_user_lang executes correct query."""
        mock_db = MagicMock()
        mock_db.execute_query_safe.return_value = 1

        monkeypatch.setattr("src.app_main.public.domain.db.db_in_process.Database", lambda db_data: mock_db)

        db = InProcessDB(db_config)
        result = db.delete_by_title_user_lang("TestPage", "TestUser", "ar")

        assert result is True
        mock_db.execute_query_safe.assert_called_with(
            "DELETE FROM in_process WHERE title = %s AND user = %s AND lang = %s",
            ("TestPage", "TestUser", "ar"),
        )
