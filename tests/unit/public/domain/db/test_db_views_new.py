"""
Unit tests for db/db_views_new.py module.

Tests for ViewsNewDB database operations.
"""

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.config import DbConfig
from src.app_main.public.domain.db.db_views_new import (
    ViewsNewDB,
    ViewsNewRecord,
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
def sample_views_row():
    """Fixture for a sample views_new row from database."""
    return {
        "id": 1,
        "target": "TestPage",
        "lang": "ar",
        "year": 2024,
        "views": 1000,
    }


class TestViewsNewDB:
    """Tests for ViewsNewDB class."""

    def test_list_returns_all_records(self, monkeypatch, db_config, sample_views_row):
        """Test that list returns all views_new records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_views_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_views_new.Database", lambda db_data: mock_db)

        db = ViewsNewDB(db_config)
        result = db.list()

        assert len(result) == 1
        assert all(isinstance(r, ViewsNewRecord) for r in result)
        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM views_new ORDER BY id ASC")

    def test_list_by_target(self, monkeypatch, db_config, sample_views_row):
        """Test that list_by_target returns filtered records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_views_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_views_new.Database", lambda db_data: mock_db)

        db = ViewsNewDB(db_config)
        result = db.list_by_target("TestPage")

        assert len(result) == 1
        mock_db.fetch_query_safe.assert_called_with(
            "SELECT * FROM views_new WHERE target = %s ORDER BY year DESC",
            ("TestPage",),
        )

    def test_list_by_lang(self, monkeypatch, db_config, sample_views_row):
        """Test that list_by_lang returns filtered records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_views_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_views_new.Database", lambda db_data: mock_db)

        db = ViewsNewDB(db_config)
        result = db.list_by_lang("ar")

        assert len(result) == 1
        mock_db.fetch_query_safe.assert_called_with(
            "SELECT * FROM views_new WHERE lang = %s ORDER BY id ASC",
            ("ar",),
        )

    def test_add_requires_non_empty_target(self, monkeypatch, db_config):
        """Test that add requires non-empty target."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_views_new.Database", lambda db_data: mock_db)

        db = ViewsNewDB(db_config)
        with pytest.raises(ValueError, match="Target is required"):
            db.add("", "ar", 2024)

    def test_add_requires_non_empty_lang(self, monkeypatch, db_config):
        """Test that add requires non-empty lang."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_views_new.Database", lambda db_data: mock_db)

        db = ViewsNewDB(db_config)
        with pytest.raises(ValueError, match="Language is required"):
            db.add("Test", "", 2024)

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_views_new.Database", lambda db_data: mock_db)

        db = ViewsNewDB(db_config)
        result = db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_target_lang_year_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_target_lang_year returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_views_new.Database", lambda db_data: mock_db)

        db = ViewsNewDB(db_config)
        result = db.fetch_by_target_lang_year("Missing", "ar", 2024)

        assert result is None

    def test_update_raises_when_not_found(self, monkeypatch, db_config):
        """Test that update raises ValueError when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_views_new.Database", lambda db_data: mock_db)

        db = ViewsNewDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            db.update(999)

    def test_delete_returns_record(self, monkeypatch, db_config, sample_views_row):
        """Test that delete returns the deleted record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_views_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_views_new.Database", lambda db_data: mock_db)

        db = ViewsNewDB(db_config)
        result = db.delete(1)

        assert result.id == 1
        mock_db.execute_query_safe.assert_called_with("DELETE FROM views_new WHERE id = %s", (1,))

    def test_add_or_update_executes_upsert(self, monkeypatch, db_config, sample_views_row):
        """Test that add_or_update executes correct upsert query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_views_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_views_new.Database", lambda db_data: mock_db)

        db = ViewsNewDB(db_config)
        db.add_or_update("TestPage", "ar", 2024, views=2000)

        call_args = mock_db.execute_query_safe.call_args
        assert "INSERT INTO views_new" in call_args[0][0]
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]
