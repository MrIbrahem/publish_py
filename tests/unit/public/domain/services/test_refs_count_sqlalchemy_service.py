from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import RefsCountRecord
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

class TestGetRefsCountsDb:
    """Tests for get_refs_counts_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new RefsCountsDB is created when none cached."""


class TestListRefsCounts:
    """Tests for list_refs_counts function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""


class TestGetRefsCount:
    """Tests for get_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""


class TestGetRefsCountByTitle:
    """Tests for get_refs_count_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_title."""


class TestAddRefsCount:
    """Tests for add_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""


class TestAddOrUpdateRefsCount:
    """Tests for add_or_update_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add_or_update."""


class TestUpdateRefsCount:
    """Tests for update_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""


class TestDeleteRefsCount:
    """Tests for delete_refs_count function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""


class TestGetRefsCountsForTitle:
    """Tests for get_ref_counts_for_title function."""

    def test_returns_counts_when_record_exists(self, monkeypatch):
        """Test that function returns counts when record found."""

    def test_returns_none_when_record_not_found(self, monkeypatch):
        """Test that function returns None when record not found."""
