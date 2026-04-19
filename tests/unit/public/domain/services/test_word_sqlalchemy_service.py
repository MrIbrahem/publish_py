from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.domain_models import WordRecord
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


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.sqlalchemy_app.shared.domain.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


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


class TestListWords:
    """Tests for list_words function."""

    def test_returns_list_of_words(self, monkeypatch):
        """Test that function returns list from store."""
        add_word("t1")
        add_word("t2")
        result = list_words()
        assert len(result) >= 2


class TestGetWord:
    """Tests for get_word function."""

    def test_delegates_to_store_fetch_by_id(self, monkeypatch):
        """Test that function returns record by ID."""
        w = add_word("t1")
        result = get_word(w.w_id)
        assert isinstance(result, WordRecord)
        assert result.w_title == "t1"

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when word not found."""
        assert get_word(999) is None


class TestGetWordByTitle:
    """Tests for get_word_by_title function."""

    def test_delegates_to_store_fetch_by_title(self, monkeypatch):
        """Test that function returns record by title."""
        add_word("t1")
        result = get_word_by_title("t1")
        assert result.w_title == "t1"


class TestAddWord:
    """Tests for add_word function."""

    def test_delegates_to_store_add(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_word("t1", 100, 200)
        assert record.w_title == "t1"
        assert record.w_lead_words == 100

    def test_passes_optional_params(self, monkeypatch):
        """Test that optional params are passed correctly."""
        record = add_word("t1", w_lead_words=50)
        assert record.w_lead_words == 50


class TestAddOrUpdateWord:
    """Tests for add_or_update_word function."""

    def test_delegates_to_store_add_or_update(self, monkeypatch):
        """Test that function upserts record."""
        add_word("t1", 1, 2)
        record = add_or_update_word("t1", 3, 4)
        assert record.w_lead_words == 3
        assert len(list_words()) == 1


class TestUpdateWord:
    """Tests for update_word function."""

    def test_delegates_to_store_update(self, monkeypatch):
        """Test that function updates and returns record."""
        w = add_word("t1", 1, 2)
        updated = update_word(w.w_id, w_lead_words=3)
        assert updated.w_lead_words == 3


class TestDeleteWord:
    """Tests for delete_word function."""

    def test_delegates_to_store_delete(self, monkeypatch):
        """Test that function deletes the record."""
        w = add_word("t1")
        delete_word(w.w_id)
        assert get_word(w.w_id) is None


class TestGetWordCountsForTitle:
    """Tests for get_word_counts_for_title function."""

    def test_returns_counts_when_record_exists(self, monkeypatch):
        """Test that function returns word counts when record found."""
        add_word("t1", 100, 200)
        lead, all_w = get_word_counts_for_title("t1")
        assert lead == 100
        assert all_w == 200

    def test_returns_none_when_record_not_found(self, monkeypatch):
        """Test that function returns None counts when record not found."""
        lead, all_w = get_word_counts_for_title("ghost")
        assert lead is None
        assert all_w is None
