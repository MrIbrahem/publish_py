"""
Unit tests for db/db_refs_counts.py module.

Tests for RefsCountsDB database operations.
"""

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.config import DbConfig
from src.app_main.public.domain.db.db_refs_counts import (
    RefsCountRecord,
    RefsCountsDB,
)


@pytest.fixture
def sample_refs_row():
    """Fixture for a sample refs_count row from database."""
    return {
        "r_id": 1,
        "r_title": "TestPage",
        "r_lead_refs": 5,
        "r_all_refs": 20,
    }


class TestRefsCountsDB:
    """Tests for RefsCountsDB class."""

    def test_list_returns_all_records(self, monkeypatch, db_config, sample_refs_row):
        """Test that list returns all refs_count records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            sample_refs_row,
            {**sample_refs_row, "r_id": 2, "r_title": "Page2"},
        ]

        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        result = db.list()

        assert len(result) == 2
        assert all(isinstance(r, RefsCountRecord) for r in result)
        assert result[0].r_id == 1
        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM refs_counts ORDER BY r_id ASC")

    def test_add_requires_non_empty_title(self, monkeypatch, db_config):
        """Test that add requires non-empty title."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        with pytest.raises(ValueError, match="Title is required"):
            db.add("")

    def test_add_strips_whitespace(self, monkeypatch, db_config):
        """Test that add strips whitespace from title."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"r_id": 1, "r_title": "TestPage"}]

        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        db.add("  TestPage  ")

        call_args = mock_db.execute_query.call_args
        assert "TestPage" in call_args[0][1]

    def test_add_raises_on_duplicate(self, monkeypatch, db_config):
        """Test that add raises ValueError on duplicate."""
        mock_db = MagicMock()
        mock_db.execute_query.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")

        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        with pytest.raises(ValueError, match="already exists"):
            db.add("TestPage")

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        result = db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_id_returns_record(self, monkeypatch, db_config, sample_refs_row):
        """Test that fetch_by_id returns record when found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_refs_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        result = db.fetch_by_id(1)

        assert result is not None
        assert result.r_id == 1

    def test_fetch_by_title_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_title returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        result = db.fetch_by_title("Missing")

        assert result is None

    def test_update_returns_unchanged_when_no_kwargs(self, monkeypatch, db_config, sample_refs_row):
        """Test that update returns record unchanged when no kwargs."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_refs_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        result = db.update(1)

        mock_db.execute_query_safe.assert_not_called()
        assert result.r_id == 1

    def test_update_executes_update_query(self, monkeypatch, db_config, sample_refs_row):
        """Test that update executes correct UPDATE query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_refs_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        db.update(1, r_lead_refs=10, r_all_refs=50)

        call_args = mock_db.execute_query_safe.call_args
        assert "UPDATE refs_counts SET" in call_args[0][0]
        assert call_args[0][1] == (10, 50, 1)

    def test_update_raises_when_not_found(self, monkeypatch, db_config):
        """Test that update raises ValueError when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            db.update(999)

    def test_delete_returns_record(self, monkeypatch, db_config, sample_refs_row):
        """Test that delete returns the deleted record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_refs_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        result = db.delete(1)

        assert result.r_id == 1
        mock_db.execute_query_safe.assert_called_with("DELETE FROM refs_counts WHERE r_id = %s", (1,))

    def test_delete_raises_when_not_found(self, monkeypatch, db_config):
        """Test that delete raises ValueError when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            db.delete(999)

    def test_add_or_update_executes_upsert(self, monkeypatch, db_config, sample_refs_row):
        """Test that add_or_update executes correct upsert query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_refs_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_refs_counts.Database", lambda db_data: mock_db)

        db = RefsCountsDB(db_config)
        db.add_or_update("TestPage", r_lead_refs=10, r_all_refs=50)

        call_args = mock_db.execute_query_safe.call_args
        assert "INSERT INTO refs_counts" in call_args[0][0]
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]
