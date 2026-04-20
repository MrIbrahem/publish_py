from unittest.mock import MagicMock, patch

import pytest
from src.db_models.shared_models import QidRecord
from src.sqlalchemy_app.shared.domain.models import _QidRecord
from src.sqlalchemy_app.shared.domain.services.qid_service import (
    add_qid,
    delete_qid,
    get_page_qid,
    get_title_to_qid,
    list_qids,
    update_qid,
)


def test_qid_workflow():
    # Test add
    q = add_qid("Earth", "Q2")
    assert q.title == "Earth"
    assert q.qid == "Q2"

    # Test get
    q2 = get_page_qid("Earth")
    assert q2.qid == "Q2"

    # Test list
    all_q = list_qids()
    assert any(x.title == "Earth" for x in all_q)

    # Test mapping
    mapping = get_title_to_qid()
    assert mapping["Earth"] == "Q2"

    # Test update
    updated = update_qid(q.id, "World", "Q2")
    assert updated.title == "World"

    # Test delete
    delete_qid(q.id)
    assert get_page_qid("World") is None


class TestGetPageQid:
    """Tests for get_page_qid function."""

    def test_returns_qid_record(self, monkeypatch):
        """Test that function returns a QidRecord."""
        add_qid("Mars", "Q111")
        result = get_page_qid("Mars")
        assert isinstance(result, QidRecord)
        assert result.qid == "Q111"

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when QID not found."""
        result = get_page_qid("Nonexistent Planet")
        assert result is None


class TestAddQid:
    """Tests for add_qid function."""

    def test_adds_qid_and_returns_record(self, monkeypatch):
        """Test that add_qid adds a QID and returns the record."""
        record = add_qid("Jupiter", "Q121")
        assert record.title == "Jupiter"
        assert record.qid == "Q121"

    def test_updates_existing_qid(self, monkeypatch):
        add_qid("Venus", "Q1")
        updated = add_qid("Venus", "Q2")
        assert updated.qid == "Q2"


class TestUpdateQid:
    """Tests for update_qid function."""

    def test_updates_qid_and_returns_record(self, monkeypatch):
        """Test that update_qid updates and returns the record."""
        q = add_qid("Saturn", "Q193")
        updated = update_qid(q.id, "Saturnian System", "Q193")
        assert updated.title == "Saturnian System"
        assert updated.qid == "Q193"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_qid(9999, "T", "Q1")


class TestDeleteQid:
    """Tests for delete_qid function."""

    def test_deletes_qid(self, monkeypatch):
        """Test that delete_qid calls store delete."""
        q = add_qid("Uranus", "Q324")
        delete_qid(q.id)
        assert not any(x.id == q.id for x in list_qids())

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_qid(9999)


class TestListQids:
    """Tests for list_qids function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_qids returns all records."""
        add_qid("Neptune", "Q332")
        add_qid("Pluto", "Q339")
        result = list_qids()
        assert len(result) >= 2

    def test_returns_empty_list_when_no_records(self, monkeypatch):
        """Test that list_qids returns empty list when no records exist."""
        result = list_qids()
        assert result == []


class TestGetTitleToQid:
    """Tests for get_title_to_qid function."""

    def test_returns_title_to_qid_mapping(self, monkeypatch):
        """Test that get_title_to_qid returns correct mapping."""
        add_qid("Sun", "Q525")
        add_qid("Moon", "Q405")
        mapping = get_title_to_qid()
        assert mapping["Sun"] == "Q525"
        assert mapping["Moon"] == "Q405"

    def test_handles_empty_qid(self, monkeypatch):
        """Test that get_title_to_qid handles empty QID values."""
        pass
