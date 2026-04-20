from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.models import _RefsCountRecord
from src.sqlalchemy_app.public.services.refs_count_service import (
    add_or_update_refs_count,
    add_refs_count,
    delete_refs_count,
    get_ref_counts_for_title,
    get_refs_count,
    get_refs_count_by_title,
    list_refs_counts,
    update_refs_count,
)
from src.db_models.public_models import RefsCountRecord


def test_refs_count_workflow():
    # Test add
    r = add_refs_count("Aspirin", 15, 120)
    assert r.r_title == "Aspirin"
    assert r.r_lead_refs == 15

    # Test get
    r2 = get_refs_count(r.r_id)
    assert r2.r_title == "Aspirin"

    # Test get by title
    r3 = get_refs_count_by_title("Aspirin")
    assert r3.r_id == r.r_id

    # Test get_ref_counts_for_title
    lead, all_refs = get_ref_counts_for_title("Aspirin")
    assert lead == 15
    assert all_refs == 120

    # Test list
    all_r = list_refs_counts()
    assert any(x.r_title == "Aspirin" for x in all_r)

    # Test update
    updated = update_refs_count(r.r_id, r_lead_refs=20)
    assert updated.r_lead_refs == 20

    # Test add_or_update
    r4 = add_or_update_refs_count("Aspirin", 25, 150)
    assert r4.r_lead_refs == 25

    # Test delete
    delete_refs_count(r.r_id)
    assert get_refs_count(r.r_id) is None


class TestListRefsCounts:
    """Tests for list_refs_counts function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_refs_count("Paracetamol")
        add_refs_count("Ibuprofen")
        result = list_refs_counts()
        assert len(result) >= 2


class TestGetRefsCount:
    """Tests for get_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        r = add_refs_count("Insulin")
        result = get_refs_count(r.r_id)
        assert isinstance(result, RefsCountRecord)
        assert result.r_title == "Insulin"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_refs_count(9999) is None


class TestGetRefsCountByTitle:
    """Tests for get_refs_count_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title."""
        add_refs_count("Penicillin")
        result = get_refs_count_by_title("Penicillin")
        assert result.r_title == "Penicillin"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_refs_count_by_title("Ghost") is None


class TestAddRefsCount:
    """Tests for add_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_refs_count("Morphine", 10, 80)
        assert record.r_title == "Morphine"
        assert record.r_lead_refs == 10
        assert record.r_all_refs == 80

    def test_raises_error_if_exists(self, monkeypatch):
        add_refs_count("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            add_refs_count("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_refs_count("")


class TestAddOrUpdateRefsCount:
    """Tests for add_or_update_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        add_refs_count("Dopamine", 5, 40)
        record = add_or_update_refs_count("Dopamine", 8, 50)
        assert record.r_lead_refs == 8
        assert record.r_all_refs == 50
        assert len(list_refs_counts()) == 1

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_or_update_refs_count(" ")


class TestUpdateRefsCount:
    """Tests for update_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        r = add_refs_count("Adrenaline", 2, 20)
        updated = update_refs_count(r.r_id, r_lead_refs=5)
        assert updated.r_lead_refs == 5

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        r = add_refs_count("No_Change")
        result = update_refs_count(r.r_id)
        assert result.r_title == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_refs_count(9999, r_lead_refs=10)


class TestDeleteRefsCount:
    """Tests for delete_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        r = add_refs_count("Diazepam")
        delete_refs_count(r.r_id)
        assert get_refs_count(r.r_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_refs_count(9999)


class TestGetRefsCountsForTitle:
    """Tests for get_ref_counts_for_title function."""

    def test_returns_counts_when_record_exists(self, monkeypatch):
        """Test that function returns counts when record found."""
        add_refs_count("Caffeine", 30, 200)
        lead, all_refs = get_ref_counts_for_title("Caffeine")
        assert lead == 30
        assert all_refs == 200

    def test_returns_none_when_record_not_found(self, monkeypatch):
        """Test that function returns None when record not found."""
        lead, all_refs = get_ref_counts_for_title("Ghost_Article")
        assert lead is None
        assert all_refs is None
