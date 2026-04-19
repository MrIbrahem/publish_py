from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.domain_models import RefsCountRecord
from src.sqlalchemy_app.public.domain.models import _RefsCountRecord
from src.sqlalchemy_app.public.domain.services.refs_count_service import (
    add_or_update_refs_count,
    add_refs_count,
    delete_refs_count,
    get_ref_counts_for_title,
    get_refs_count,
    get_refs_count_by_title,
    list_refs_counts,
    update_refs_count,
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


def test_refs_count_workflow():
    # Test add
    r = add_refs_count("test_page", 10, 50)
    assert r.r_title == "test_page"
    assert r.r_lead_refs == 10

    # Test get
    r2 = get_refs_count(r.r_id)
    assert r2.r_title == "test_page"

    # Test get by title
    r3 = get_refs_count_by_title("test_page")
    assert r3.r_id == r.r_id

    # Test get_ref_counts_for_title
    lead, all_refs = get_ref_counts_for_title("test_page")
    assert lead == 10
    assert all_refs == 50

    # Test list
    all_r = list_refs_counts()
    assert any(x.r_title == "test_page" for x in all_r)

    # Test update
    updated = update_refs_count(r.r_id, r_lead_refs=20)
    assert updated.r_lead_refs == 20

    # Test add_or_update
    r4 = add_or_update_refs_count("test_page", 30, 60)
    assert r4.r_lead_refs == 30

    # Test delete
    delete_refs_count(r.r_id)
    assert get_refs_count(r.r_id) is None


class TestListRefsCounts:
    """Tests for list_refs_counts function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_refs_count("t1")
        add_refs_count("t2")
        result = list_refs_counts()
        assert len(result) >= 2


class TestGetRefsCount:
    """Tests for get_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        r = add_refs_count("t1")
        result = get_refs_count(r.r_id)
        assert isinstance(result, RefsCountRecord)
        assert result.r_title == "t1"


class TestGetRefsCountByTitle:
    """Tests for get_refs_count_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title."""
        add_refs_count("t1")
        result = get_refs_count_by_title("t1")
        assert result.r_title == "t1"


class TestAddRefsCount:
    """Tests for add_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_refs_count("t1", 5, 10)
        assert record.r_title == "t1"
        assert record.r_lead_refs == 5
        assert record.r_all_refs == 10


class TestAddOrUpdateRefsCount:
    """Tests for add_or_update_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        add_refs_count("t1", 1, 2)
        record = add_or_update_refs_count("t1", 3, 4)
        assert record.r_lead_refs == 3
        assert record.r_all_refs == 4
        assert len(list_refs_counts()) == 1


class TestUpdateRefsCount:
    """Tests for update_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        r = add_refs_count("t1", 1, 2)
        updated = update_refs_count(r.r_id, r_lead_refs=3)
        assert updated.r_lead_refs == 3


class TestDeleteRefsCount:
    """Tests for delete_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        r = add_refs_count("t1")
        delete_refs_count(r.r_id)
        assert get_refs_count(r.r_id) is None


class TestGetRefsCountsForTitle:
    """Tests for get_ref_counts_for_title function."""

    def test_returns_counts_when_record_exists(self, monkeypatch):
        """Test that function returns counts when record found."""
        add_refs_count("t1", 10, 20)
        lead, all_refs = get_ref_counts_for_title("t1")
        assert lead == 10
        assert all_refs == 20

    def test_returns_none_when_record_not_found(self, monkeypatch):
        """Test that function returns None when record not found."""
        lead, all_refs = get_ref_counts_for_title("ghost")
        assert lead is None
        assert all_refs is None
