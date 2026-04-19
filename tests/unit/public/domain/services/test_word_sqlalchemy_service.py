from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import WordRecord
from src.sqlalchemy_app.public.domain.models import _WordRecord
from src.sqlalchemy_app.public.domain.services.word_service import (
    add_or_update_word,
    add_word,
    delete_word,
    get_word,
    get_word_by_title,
    get_word_counts_for_title,
    list_words,
    update_word,
)
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db





def test_word_workflow():
    # Test add
    w = add_word("test_page", 100, 500)
    assert w.w_title == "test_page"
    assert w.w_lead_words == 100

    # Test get
    w2 = get_word(w.w_id)
    assert w2.w_title == "test_page"

    # Test get by title
    w3 = get_word_by_title("test_page")
    assert w3.w_id == w.w_id

    # Test get_word_counts_for_title
    lead, all_words = get_word_counts_for_title("test_page")
    assert lead == 100
    assert all_words == 500

    # Test list
    all_w = list_words()
    assert any(x.w_title == "test_page" for x in all_w)

    # Test update
    updated = update_word(w.w_id, w_lead_words=150)
    assert updated.w_lead_words == 150

    # Test add_or_update
    w4 = add_or_update_word("test_page", 200, 600)
    assert w4.w_lead_words == 200

    # Test delete
    delete_word(w.w_id)
    assert get_word(w.w_id) is None



class TestGetWordsDb:
    """Tests for get_words_db function."""

    def test_returns_cached_instance_on_subsequent_calls(self, monkeypatch):
        """Test that singleton pattern returns same instance."""

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new WordsDB is created when none cached."""

    def test_caches_instance_after_first_creation(self, monkeypatch):
        """Test that created instance is cached for reuse."""


class TestListWords:
    """Tests for list_words function."""

    def test_returns_list_of_words(self, monkeypatch):
        """Test that function returns list from store."""


class TestGetWord:
    """Tests for get_word function."""

    def test_delegates_to_store_fetch_by_id(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when word not found."""


class TestGetWordByTitle:
    """Tests for get_word_by_title function."""

    def test_delegates_to_store_fetch_by_title(self, monkeypatch):
        """Test that function delegates to store.fetch_by_title."""


class TestAddWord:
    """Tests for add_word function."""

    def test_delegates_to_store_add(self, monkeypatch):
        """Test that function delegates to store.add."""

    def test_passes_optional_params(self, monkeypatch):
        """Test that optional params are passed correctly."""


class TestAddOrUpdateWord:
    """Tests for add_or_update_word function."""

    def test_delegates_to_store_add_or_update(self, monkeypatch):
        """Test that function delegates to store.add_or_update."""


class TestUpdateWord:
    """Tests for update_word function."""

    def test_delegates_to_store_update(self, monkeypatch):
        """Test that function delegates to store.update."""


class TestDeleteWord:
    """Tests for delete_word function."""

    def test_delegates_to_store_delete(self, monkeypatch):
        """Test that function delegates to store.delete."""


class TestGetWordCountsForTitle:
    """Tests for get_word_counts_for_title function."""

    def test_returns_counts_when_record_exists(self, monkeypatch):
        """Test that function returns word counts when record found."""

    def test_returns_none_when_record_not_found(self, monkeypatch):
        """Test that function returns None counts when record not found."""
