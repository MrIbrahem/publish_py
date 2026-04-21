from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.db_models import WordRecord
from src.sqlalchemy_app.public.services.word_service import (
    add_or_update_word,
    add_word,
    delete_word,
    get_word,
    get_word_by_title,
    get_word_counts_for_title,
    list_words,
    update_word,
)
from src.sqlalchemy_app.sqlalchemy_models import _WordRecord


def test_word_workflow():
    # Test add
    w = add_word("Human anatomy", 500, 5000)
    assert w.w_title == "Human anatomy"
    assert w.w_lead_words == 500

    # Test get
    w2 = get_word(w.w_id)
    assert w2.w_title == "Human anatomy"

    # Test get by title
    w3 = get_word_by_title("Human anatomy")
    assert w3.w_id == w.w_id

    # Test get_word_counts_for_title
    lead, all_words = get_word_counts_for_title("Human anatomy")
    assert lead == 500
    assert all_words == 5000

    # Test list
    all_w = list_words()
    assert any(x.w_title == "Human anatomy" for x in all_w)

    # Test update
    updated = update_word(w.w_id, w_lead_words=600)
    assert updated.w_lead_words == 600

    # Test add_or_update
    w4 = add_or_update_word("Human anatomy", 700, 6000)
    assert w4.w_lead_words == 700

    # Test delete
    delete_word(w.w_id)
    assert get_word(w.w_id) is None


class TestListWords:
    """Tests for list_words function."""

    def test_returns_list_of_words(self, monkeypatch):
        """Test that function returns list from store."""
        add_word("Microscope")
        add_word("Stethoscope")
        result = list_words()
        assert len(result) >= 2


class TestGetWord:
    """Tests for get_word function."""

    def test_delegates_to_store_fetch_by_id(self, monkeypatch):
        """Test that function returns record by ID."""
        w = add_word("Cell structure")
        result = get_word(w.w_id)
        assert isinstance(result, WordRecord)
        assert result.w_title == "Cell structure"

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when word not found."""
        assert get_word(77777) is None


class TestGetWordByTitle:
    """Tests for get_word_by_title function."""

    def test_delegates_to_store_fetch_by_title(self, monkeypatch):
        """Test that function returns record by title."""
        add_word("DNA replication")
        result = get_word_by_title("DNA replication")
        assert result.w_title == "DNA replication"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_word_by_title("Ghost") is None


class TestAddWord:
    """Tests for add_word function."""

    def test_delegates_to_store_add(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_word("Protein folding", 300, 1500)
        assert record.w_title == "Protein folding"
        assert record.w_lead_words == 300

    def test_passes_optional_params(self, monkeypatch):
        """Test that optional params are passed correctly."""
        record = add_word("T1", w_lead_words=50)
        assert record.w_lead_words == 50

    def test_raises_error_if_exists(self, monkeypatch):
        add_word("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            add_word("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_word("")


class TestAddOrUpdateWord:
    """Tests for add_or_update_word function."""

    def test_delegates_to_store_add_or_update(self, monkeypatch):
        """Test that function upserts record."""
        add_word("Antibody", 100, 1000)
        record = add_or_update_word("Antibody", 150, 1200)
        assert record.w_lead_words == 150
        assert len(list_words()) == 1

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_or_update_word("  ")


class TestUpdateWord:
    """Tests for update_word function."""

    def test_delegates_to_store_update(self, monkeypatch):
        """Test that function updates and returns record."""
        w = add_word("Antigen", 50, 500)
        updated = update_word(w.w_id, w_lead_words=75)
        assert updated.w_lead_words == 75

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        w = add_word("No_Change")
        result = update_word(w.w_id)
        assert result.w_title == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_word(9999, w_lead_words=10)


class TestDeleteWord:
    """Tests for delete_word function."""

    def test_delegates_to_store_delete(self, monkeypatch):
        """Test that function deletes the record."""
        w = add_word("T-cell")
        delete_word(w.w_id)
        assert get_word(w.w_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_word(9999)


class TestGetWordCountsForTitle:
    """Tests for get_word_counts_for_title function."""

    def test_returns_counts_when_record_exists(self, monkeypatch):
        """Test that function returns word counts when record found."""
        add_word("B-cell", 80, 800)
        lead, all_w = get_word_counts_for_title("B-cell")
        assert lead == 80
        assert all_w == 800

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None counts when record not found."""
        lead, all_w = get_word_counts_for_title("Ghost_Article")
        assert lead is None
        assert all_w is None
