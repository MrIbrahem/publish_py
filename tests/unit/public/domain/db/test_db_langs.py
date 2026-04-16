"""
Unit tests for db/db_langs.py module.

Tests for LangsDB database operations.
"""

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.config import DbConfig
from src.app_main.public.domain.db.db_langs import (
    LangRecord,
    LangsDB,
)


@pytest.fixture
def db_config():
    """Fixture for DbConfig instance."""
    return DbConfig(
        db_name="test_db",
        db_host="localhost",
        db_user="user",
        db_password="pass",
    )


@pytest.fixture
def sample_lang_row():
    """Fixture for a sample lang row from database."""
    return {
        "lang_id": 1,
        "code": "ar",
        "autonym": "العربية",
        "name": "Arabic",
    }


class TestLangsDB:
    """Tests for LangsDB class."""

    def test_list_returns_all_records(self, monkeypatch, db_config, sample_lang_row):
        """Test that list returns all lang records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_lang_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_langs.Database", lambda db_data: mock_db)

        db = LangsDB(db_config)
        result = db.list()

        assert len(result) == 1
        assert all(isinstance(r, LangRecord) for r in result)
        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM langs ORDER BY lang_id ASC")

    def test_add_requires_non_empty_code(self, monkeypatch, db_config):
        """Test that add requires non-empty code."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_langs.Database", lambda db_data: mock_db)

        db = LangsDB(db_config)
        with pytest.raises(ValueError, match="Language code is required"):
            db.add("", "Autonym", "Name")

    def test_add_strips_whitespace(self, monkeypatch, db_config):
        """Test that add strips whitespace from code."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"lang_id": 1, "code": "ar"}]

        monkeypatch.setattr("src.app_main.public.domain.db.db_langs.Database", lambda db_data: mock_db)

        db = LangsDB(db_config)
        db.add("  ar  ", "العربية", "Arabic")

        call_args = mock_db.execute_query.call_args
        assert "ar" in call_args[0][1]

    def test_add_raises_on_duplicate(self, monkeypatch, db_config):
        """Test that add raises ValueError on duplicate."""
        mock_db = MagicMock()
        mock_db.execute_query.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")

        monkeypatch.setattr("src.app_main.public.domain.db.db_langs.Database", lambda db_data: mock_db)

        db = LangsDB(db_config)
        with pytest.raises(ValueError, match="already exists"):
            db.add("ar", "العربية", "Arabic")

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_langs.Database", lambda db_data: mock_db)

        db = LangsDB(db_config)
        result = db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_code_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_code returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_langs.Database", lambda db_data: mock_db)

        db = LangsDB(db_config)
        result = db.fetch_by_code("xyz")

        assert result is None

    def test_update_raises_when_not_found(self, monkeypatch, db_config):
        """Test that update raises ValueError when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_langs.Database", lambda db_data: mock_db)

        db = LangsDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            db.update(999)

    def test_delete_returns_record(self, monkeypatch, db_config, sample_lang_row):
        """Test that delete returns the deleted record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_lang_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_langs.Database", lambda db_data: mock_db)

        db = LangsDB(db_config)
        result = db.delete(1)

        assert result.lang_id == 1
        mock_db.execute_query_safe.assert_called_with("DELETE FROM langs WHERE lang_id = %s", (1,))

    def test_add_or_update_executes_upsert(self, monkeypatch, db_config, sample_lang_row):
        """Test that add_or_update executes correct upsert query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_lang_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_langs.Database", lambda db_data: mock_db)

        db = LangsDB(db_config)
        db.add_or_update("ar", "العربية", "Arabic")

        call_args = mock_db.execute_query_safe.call_args
        assert "INSERT INTO langs" in call_args[0][0]
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]
