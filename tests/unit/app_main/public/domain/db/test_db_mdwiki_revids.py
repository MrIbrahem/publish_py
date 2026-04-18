"""
Unit tests for db/db_mdwiki_revids.py module.

Tests for MdwikiRevidsDB database operations.
"""

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.config import DbConfig
from src.app_main.public.domain.db.db_mdwiki_revids import (
    MdwikiRevidRecord,
    MdwikiRevidsDB,
)


@pytest.fixture
def sample_revid_row():
    """Fixture for a sample mdwiki_revids row from database."""
    return {
        "title": "TestPage",
        "revid": 12345,
    }


class TestMdwikiRevidsDB:
    """Tests for MdwikiRevidsDB class."""

    def test_list_returns_all_records(self, monkeypatch, db_config, sample_revid_row):
        """Test that list returns all mdwiki_revid records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_revid_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_mdwiki_revids.Database", lambda db_data: mock_db)

        db = MdwikiRevidsDB(db_config)
        result = db.list()

        assert len(result) == 1
        assert all(isinstance(r, MdwikiRevidRecord) for r in result)
        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM mdwiki_revids ORDER BY title ASC")

    def test_add_requires_non_empty_title(self, monkeypatch, db_config):
        """Test that add requires non-empty title."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_mdwiki_revids.Database", lambda db_data: mock_db)

        db = MdwikiRevidsDB(db_config)
        with pytest.raises(ValueError, match="Title is required"):
            db.add("", 12345)

    def test_add_strips_whitespace(self, monkeypatch, db_config):
        """Test that add strips whitespace from title."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"title": "TestPage", "revid": 12345}]

        monkeypatch.setattr("src.app_main.public.domain.db.db_mdwiki_revids.Database", lambda db_data: mock_db)

        db = MdwikiRevidsDB(db_config)
        db.add("  TestPage  ", 12345)

        call_args = mock_db.execute_query.call_args
        assert "TestPage" in call_args[0][1]

    def test_add_raises_on_duplicate(self, monkeypatch, db_config):
        """Test that add raises ValueError on duplicate."""
        mock_db = MagicMock()
        mock_db.execute_query.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")

        monkeypatch.setattr("src.app_main.public.domain.db.db_mdwiki_revids.Database", lambda db_data: mock_db)

        db = MdwikiRevidsDB(db_config)
        with pytest.raises(ValueError, match="already exists"):
            db.add("TestPage", 12345)

    def test_fetch_by_title_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_title returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_mdwiki_revids.Database", lambda db_data: mock_db)

        db = MdwikiRevidsDB(db_config)
        result = db.fetch_by_title("Missing")

        assert result is None

    def test_update_raises_when_not_found(self, monkeypatch, db_config):
        """Test that update raises ValueError when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_mdwiki_revids.Database", lambda db_data: mock_db)

        db = MdwikiRevidsDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            db.update("Missing", 54321)

    def test_update_executes_update_query(self, monkeypatch, db_config, sample_revid_row):
        """Test that update executes correct UPDATE query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_revid_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_mdwiki_revids.Database", lambda db_data: mock_db)

        db = MdwikiRevidsDB(db_config)
        db.update("TestPage", 54321)

        call_args = mock_db.execute_query_safe.call_args
        assert "UPDATE mdwiki_revids SET revid = %s WHERE title = %s" in call_args[0][0]
        assert call_args[0][1] == (54321, "TestPage")

    def test_delete_raises_when_not_found(self, monkeypatch, db_config):
        """Test that delete raises ValueError when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_mdwiki_revids.Database", lambda db_data: mock_db)

        db = MdwikiRevidsDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            db.delete("Missing")

    def test_delete_executes_delete_query(self, monkeypatch, db_config, sample_revid_row):
        """Test that delete executes correct DELETE query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_revid_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_mdwiki_revids.Database", lambda db_data: mock_db)

        db = MdwikiRevidsDB(db_config)
        result = db.delete("TestPage")

        assert result.title == "TestPage"
        mock_db.execute_query_safe.assert_called_with("DELETE FROM mdwiki_revids WHERE title = %s", ("TestPage",))

    def test_add_or_update_executes_upsert(self, monkeypatch, db_config, sample_revid_row):
        """Test that add_or_update executes correct upsert query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_revid_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_mdwiki_revids.Database", lambda db_data: mock_db)

        db = MdwikiRevidsDB(db_config)
        db.add_or_update("TestPage", 54321)

        call_args = mock_db.execute_query_safe.call_args
        assert "INSERT INTO mdwiki_revids" in call_args[0][0]
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]
