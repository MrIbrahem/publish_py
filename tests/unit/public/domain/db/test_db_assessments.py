"""
Unit tests for db/db_assessments.py module.

Tests for AssessmentsDB database operations.
"""

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.config import DbConfig
from src.app_main.public.domain.db.db_assessments import (
    AssessmentRecord,
    AssessmentsDB,
)





@pytest.fixture
def sample_assessment_row():
    """Fixture for a sample assessment row from database."""
    return {
        "id": 1,
        "title": "TestPage",
        "importance": "High",
    }


class TestAssessmentsDB:
    """Tests for AssessmentsDB class."""

    def test_list_returns_all_records(self, monkeypatch, db_config, sample_assessment_row):
        """Test that list returns all assessment records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_assessment_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_assessments.Database", lambda db_data: mock_db)

        db = AssessmentsDB(db_config)
        result = db.list()

        assert len(result) == 1
        assert all(isinstance(r, AssessmentRecord) for r in result)
        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM assessments ORDER BY id ASC")

    def test_add_requires_non_empty_title(self, monkeypatch, db_config):
        """Test that add requires non-empty title."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_assessments.Database", lambda db_data: mock_db)

        db = AssessmentsDB(db_config)
        with pytest.raises(ValueError, match="Title is required"):
            db.add("")

    def test_add_strips_whitespace(self, monkeypatch, db_config):
        """Test that add strips whitespace from title."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "title": "TestPage"}]

        monkeypatch.setattr("src.app_main.public.domain.db.db_assessments.Database", lambda db_data: mock_db)

        db = AssessmentsDB(db_config)
        db.add("  TestPage  ")

        call_args = mock_db.execute_query.call_args
        assert "TestPage" in call_args[0][1]

    def test_add_raises_on_duplicate(self, monkeypatch, db_config):
        """Test that add raises ValueError on duplicate."""
        mock_db = MagicMock()
        mock_db.execute_query.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")

        monkeypatch.setattr("src.app_main.public.domain.db.db_assessments.Database", lambda db_data: mock_db)

        db = AssessmentsDB(db_config)
        with pytest.raises(ValueError, match="already exists"):
            db.add("TestPage")

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_assessments.Database", lambda db_data: mock_db)

        db = AssessmentsDB(db_config)
        result = db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_title_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_title returns None when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_assessments.Database", lambda db_data: mock_db)

        db = AssessmentsDB(db_config)
        result = db.fetch_by_title("Missing")

        assert result is None

    def test_update_raises_when_not_found(self, monkeypatch, db_config):
        """Test that update raises ValueError when not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_assessments.Database", lambda db_data: mock_db)

        db = AssessmentsDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            db.update(999)

    def test_delete_returns_record(self, monkeypatch, db_config, sample_assessment_row):
        """Test that delete returns the deleted record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_assessment_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_assessments.Database", lambda db_data: mock_db)

        db = AssessmentsDB(db_config)
        result = db.delete(1)

        assert result.id == 1
        mock_db.execute_query_safe.assert_called_with("DELETE FROM assessments WHERE id = %s", (1,))

    def test_add_or_update_executes_upsert(self, monkeypatch, db_config, sample_assessment_row):
        """Test that add_or_update executes correct upsert query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_assessment_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_assessments.Database", lambda db_data: mock_db)

        db = AssessmentsDB(db_config)
        db.add_or_update("TestPage", importance="Low")

        call_args = mock_db.execute_query_safe.call_args
        assert "INSERT INTO assessments" in call_args[0][0]
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]
