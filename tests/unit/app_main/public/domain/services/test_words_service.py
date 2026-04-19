"""
Unit tests for domain/services/word_service.py module.

Tests for words service layer which provides cached access to WordsDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.word_service import (
    add_or_update_word,
    add_word,
    delete_word,
    get_word,
    get_word_by_title,
    get_word_counts_for_title,
    get_words_db,
    list_words,
    update_word,
)


class TestGetWordsDb:
    """Tests for get_words_db function."""

    def test_returns_cached_instance_on_subsequent_calls(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.services.word_service._WORDS_STORE", mock_db)
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.has_db_config", lambda: True)

        result = get_words_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr("src.app_main.public.domain.services.word_service._WORDS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="WordsDB requires database configuration"):
            get_words_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new WordsDB is created when none cached."""
        monkeypatch.setattr("src.app_main.public.domain.services.word_service._WORDS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.word_service.WordsDB") as MockWordsDB:
            MockWordsDB.return_value = mock_db_instance

            result = get_words_db()

            assert result is mock_db_instance
            MockWordsDB.assert_called_once()

    def test_caches_instance_after_first_creation(self, monkeypatch):
        """Test that created instance is cached for reuse."""
        monkeypatch.setattr("src.app_main.public.domain.services.word_service._WORDS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.word_service.WordsDB") as MockWordsDB:
            MockWordsDB.return_value = mock_db_instance

            result1 = get_words_db()
            result2 = get_words_db()

            assert result1 is result2 is mock_db_instance
            MockWordsDB.assert_called_once()


class TestListWords:
    """Tests for list_words function."""

    def test_returns_list_of_words(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.get_words_db", lambda: mock_store)

        result = list_words()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestGetWord:
    """Tests for get_word function."""

    def test_delegates_to_store_fetch_by_id(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.get_words_db", lambda: mock_store)

        result = get_word(123)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(123)

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when word not found."""
        mock_store = MagicMock()
        mock_store.fetch_by_id.return_value = None
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.get_words_db", lambda: mock_store)

        result = get_word(999)

        assert result is None


class TestGetWordByTitle:
    """Tests for get_word_by_title function."""

    def test_delegates_to_store_fetch_by_title(self, monkeypatch):
        """Test that function delegates to store.fetch_by_title."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.get_words_db", lambda: mock_store)

        result = get_word_by_title("TestPage")

        assert result is mock_record
        mock_store.fetch_by_title.assert_called_once_with("TestPage")


class TestAddWord:
    """Tests for add_word function."""

    def test_delegates_to_store_add(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.get_words_db", lambda: mock_store)

        result = add_word("TestPage", w_lead_words=100, w_all_words=500)

        assert result is mock_record
        mock_store.add.assert_called_once_with("TestPage", 100, 500)

    def test_passes_optional_params(self, monkeypatch):
        """Test that optional params are passed correctly."""
        mock_store = MagicMock()
        mock_store.add.return_value = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.get_words_db", lambda: mock_store)

        add_word("TestPage")

        mock_store.add.assert_called_once_with("TestPage", None, None)


class TestAddOrUpdateWord:
    """Tests for add_or_update_word function."""

    def test_delegates_to_store_add_or_update(self, monkeypatch):
        """Test that function delegates to store.add_or_update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.get_words_db", lambda: mock_store)

        result = add_or_update_word("TestPage", w_lead_words=100, w_all_words=500)

        assert result is mock_record
        mock_store.add_or_update.assert_called_once_with("TestPage", 100, 500)


class TestUpdateWord:
    """Tests for update_word function."""

    def test_delegates_to_store_update(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.get_words_db", lambda: mock_store)

        result = update_word(1, w_lead_words=200, w_all_words=1000)

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, w_lead_words=200, w_all_words=1000)


class TestDeleteWord:
    """Tests for delete_word function."""

    def test_delegates_to_store_delete(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.get_words_db", lambda: mock_store)

        result = delete_word(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)


class TestGetWordCountsForTitle:
    """Tests for get_word_counts_for_title function."""

    def test_returns_counts_when_record_exists(self, monkeypatch):
        """Test that function returns word counts when record found."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.w_lead_words = 100
        mock_record.w_all_words = 500
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.get_words_db", lambda: mock_store)

        lead, all_words = get_word_counts_for_title("TestPage")

        assert lead == 100
        assert all_words == 500

    def test_returns_none_when_record_not_found(self, monkeypatch):
        """Test that function returns None counts when record not found."""
        mock_store = MagicMock()
        mock_store.fetch_by_title.return_value = None
        monkeypatch.setattr("src.app_main.public.domain.services.word_service.get_words_db", lambda: mock_store)

        lead, all_words = get_word_counts_for_title("MissingPage")

        assert lead is None
        assert all_words is None
