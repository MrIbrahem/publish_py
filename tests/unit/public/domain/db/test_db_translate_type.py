"""
Unit tests for db/db_translate_type.py module.

Tests for TranslateTypeDB database operations.
"""

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.config import DbConfig
from src.app_main.public.domain.db.db_translate_type import (
    TranslateTypeDB,
    TranslateTypeRecord,
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
def sample_translate_type_row():
    """Fixture for a sample translate_type row from database."""
    return {
        "tt_id": 1,
        "tt_title": "Lead",
        "tt_lead": 1,
        "tt_full": 0,
    }


class TestTranslateTypeDB:
    """Tests for TranslateTypeDB class."""

    def test_list_returns_all_records(self, monkeypatch, db_config, sample_translate_type_row):
        """Test that list returns all translate_type records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_translate_type_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_translate_type.Database", lambda db_data: mock_db)

        db = TranslateTypeDB(db_config)
        result = db.list()

        assert len(result) == 1
        assert all(isinstance(r, TranslateTypeRecord) for r in result)
        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM translate_type ORDER BY tt_id ASC")

    def test_list_lead_enabled(self, monkeypatch, db_config, sample_translate_type_row):
        """Test that list_lead_enabled returns records with lead enabled."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_translate_type_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_translate_type.Database", lambda db_data: mock_db)

        db = TranslateTypeDB(db_config)
        result = db.list_lead_enabled()

        assert len(result) == 1
        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM translate_type WHERE tt_lead = 1 ORDER BY tt_id ASC")

    def test_list_full_enabled(self, monkeypatch, db_config):
        """Test that list_full_enabled returns records with full enabled."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_translate_type.Database", lambda db_data: mock_db)

        db = TranslateTypeDB(db_config)
        result = db.list_full_enabled()

        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM translate_type WHERE tt_full = 1 ORDER BY tt_id ASC")

    def test_add_requires_non_empty_title(self, monkeypatch, db_config):
        """Test that add requires non-empty title."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_translate_type.Database", lambda db_data: mock_db)

        db = TranslateTypeDB(db_config)
        with pytest.raises(ValueError, match="Title is required"):
            db.add("")

    def test_add_strips_whitespace(self, monkeypatch, db_config):
        """Test that add strips whitespace from title."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"tt_id": 1, "tt_title": "Test"}]

        monkeypatch.setattr("src.app_main.public.domain.db.db_translate_type.Database", lambda db_data: mock_db)

        db = TranslateTypeDB(db_config)
        db.add("  Test  ")

        call_args = mock_db.execute_query.call_args
        assert "Test" in call_args[0][1]

    def test_add_raises_on_duplicate(self, monkeypatch, db_config):
        """Test that add raises ValueError on duplicate."""
        mock_db = MagicMock()
        mock_db.execute_query.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")

        monkeypatch.setattr("src.app_main.public.domain.db.db_translate_type.Database", lambda db_data: mock_db)

        db = TranslateTypeDB(db_config)
        with pytest.raises(ValueError, match="already exists"):
            db.add("Lead")

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_translate_type.Database", lambda db_data: mock_db)

        db = TranslateTypeDB(db_config)
        result = db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_title_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_title returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_translate_type.Database", lambda db_data: mock_db)

        db = TranslateTypeDB(db_config)
        result = db.fetch_by_title("Missing")

        assert result is None

    def test_update_raises_when_not_found(self, monkeypatch, db_config):
        """Test that update raises ValueError when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_translate_type.Database", lambda db_data: mock_db)

        db = TranslateTypeDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            db.update(999)

    def test_update_executes_update_query(self, monkeypatch, db_config, sample_translate_type_row):
        """Test that update executes correct UPDATE query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_translate_type_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_translate_type.Database", lambda db_data: mock_db)

        db = TranslateTypeDB(db_config)
        db.update(1, tt_full=1)

        call_args = mock_db.execute_query_safe.call_args
        assert "UPDATE translate_type SET" in call_args[0][0]
        assert call_args[0][1] == (1, 1)

    def test_delete_returns_record(self, monkeypatch, db_config, sample_translate_type_row):
        """Test that delete returns the deleted record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_translate_type_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_translate_type.Database", lambda db_data: mock_db)

        db = TranslateTypeDB(db_config)
        result = db.delete(1)

        assert result.tt_id == 1
        mock_db.execute_query_safe.assert_called_with("DELETE FROM translate_type WHERE tt_id = %s", (1,))

    def test_add_or_update_executes_upsert(self, monkeypatch, db_config, sample_translate_type_row):
        """Test that add_or_update executes correct upsert query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_translate_type_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_translate_type.Database", lambda db_data: mock_db)

        db = TranslateTypeDB(db_config)
        db.add_or_update("Lead", tt_lead=1, tt_full=1)

        call_args = mock_db.execute_query_safe.call_args
        assert "INSERT INTO translate_type" in call_args[0][0]
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]
