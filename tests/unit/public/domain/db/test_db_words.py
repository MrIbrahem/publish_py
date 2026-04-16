"""
Unit tests for db/db_words.py module.

Tests for WordsDB database operations.
"""

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.config import DbConfig
from src.app_main.public.domain.db.db_words import (
    WordRecord,
    WordsDB,
)


@pytest.fixture
def sample_word_row():
    """Fixture for a sample word row from database."""
    return {
        "w_id": 1,
        "w_title": "TestPage",
        "w_lead_words": 100,
        "w_all_words": 500,
    }


class TestWordsDB:
    """Tests for WordsDB class."""

    def test_list_returns_all_words(self, monkeypatch, db_config, sample_word_row):
        """Test that list returns all word records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            sample_word_row,
            {**sample_word_row, "w_id": 2, "w_title": "Page2"},
        ]

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        result = words_db.list()

        assert len(result) == 2
        assert all(isinstance(r, WordRecord) for r in result)
        assert result[0].w_id == 1
        assert result[1].w_id == 2
        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM words ORDER BY w_id ASC")

    def test_add_requires_non_empty_title(self, monkeypatch, db_config):
        """Test that add requires non-empty title."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        with pytest.raises(ValueError, match="Title is required"):
            words_db.add("")

        with pytest.raises(ValueError, match="Title is required"):
            words_db.add("   ")

    def test_add_strips_whitespace_from_title(self, monkeypatch, db_config):
        """Test that add strips whitespace from title."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"w_id": 1, "w_title": "TestPage"}]

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        words_db.add("  TestPage  ")

        call_args = mock_db.execute_query.call_args
        assert "TestPage" in call_args[0][1]
        assert "  TestPage  " not in call_args[0][1]

    def test_add_raises_on_duplicate(self, monkeypatch, db_config):
        """Test that add raises ValueError on duplicate title."""
        mock_db = MagicMock()
        mock_db.execute_query.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        with pytest.raises(ValueError, match="already exists"):
            words_db.add("TestPage")

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when word not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        result = words_db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_id_returns_record(self, monkeypatch, db_config, sample_word_row):
        """Test that fetch_by_id returns record when found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_word_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        result = words_db.fetch_by_id(1)

        assert result is not None
        assert result.w_id == 1
        assert result.w_title == "TestPage"

    def test_fetch_by_title_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_title returns None when word not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        result = words_db.fetch_by_title("MissingPage")

        assert result is None

    def test_fetch_by_title_returns_record(self, monkeypatch, db_config, sample_word_row):
        """Test that fetch_by_title returns record when found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_word_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        result = words_db.fetch_by_title("TestPage")

        assert result is not None
        assert result.w_id == 1
        assert result.w_title == "TestPage"

    def test_update_returns_record_unchanged_when_no_kwargs(self, monkeypatch, db_config, sample_word_row):
        """Test that update returns record unchanged when no fields to update."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_word_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        result = words_db.update(1)

        mock_db.execute_query_safe.assert_not_called()
        assert result.w_id == 1

    def test_update_executes_update_query(self, monkeypatch, db_config, sample_word_row):
        """Test that update executes correct UPDATE query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_word_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        words_db.update(1, w_lead_words=200, w_all_words=1000)

        call_args = mock_db.execute_query_safe.call_args
        assert "UPDATE words SET" in call_args[0][0]
        assert "`w_lead_words` = %s" in call_args[0][0]
        assert "`w_all_words` = %s" in call_args[0][0]
        assert call_args[0][1] == (200, 1000, 1)

    def test_update_raises_when_not_found(self, monkeypatch, db_config):
        """Test that update raises ValueError when word not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            words_db.update(999)

    def test_delete_returns_record(self, monkeypatch, db_config, sample_word_row):
        """Test that delete returns the deleted record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_word_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        result = words_db.delete(1)

        assert result.w_id == 1
        mock_db.execute_query_safe.assert_called_with(
            "DELETE FROM words WHERE w_id = %s",
            (1,),
        )

    def test_delete_raises_when_not_found(self, monkeypatch, db_config):
        """Test that delete raises ValueError when word not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            words_db.delete(999)

    def test_add_or_update_executes_upsert(self, monkeypatch, db_config, sample_word_row):
        """Test that add_or_update executes correct upsert query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_word_row]

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        words_db.add_or_update("TestPage", w_lead_words=200, w_all_words=1000)

        call_args = mock_db.execute_query_safe.call_args
        assert "INSERT INTO words" in call_args[0][0]
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]

    def test_add_or_update_requires_non_empty_title(self, monkeypatch, db_config):
        """Test that add_or_update requires non-empty title."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        with pytest.raises(ValueError, match="Title is required"):
            words_db.add_or_update("")

    def test_add_with_optional_params(self, monkeypatch, db_config, sample_word_row):
        """Test that add works with optional params."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{**sample_word_row, "w_lead_words": None, "w_all_words": None}]

        monkeypatch.setattr("src.app_main.public.domain.db.db_words.Database", lambda db_data: mock_db)

        words_db = WordsDB(db_config)
        result = words_db.add("NewPage")

        assert result is not None
        call_args = mock_db.execute_query.call_args
        assert None in call_args[0][1]
