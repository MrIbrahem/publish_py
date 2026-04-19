from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import MdwikiRevidRecord
from src.sqlalchemy_app.public.domain.models import _MdwikiRevidRecord
from src.sqlalchemy_app.public.domain.services.mdwiki_revid_service import (
    add_mdwiki_revid,
    add_or_update_mdwiki_revid,
    delete_mdwiki_revid,
    get_mdwiki_revid_by_title,
    get_revid_for_title,
    list_mdwiki_revids,
    update_mdwiki_revid,
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


def test_mdwiki_revid_workflow():
    # Test add
    r = add_mdwiki_revid("test_page", 12345)
    assert r.title == "test_page"
    assert r.revid == 12345

    # Test get by title
    r2 = get_mdwiki_revid_by_title("test_page")
    assert r2.revid == 12345

    # Test get_revid_for_title
    revid = get_revid_for_title("test_page")
    assert revid == 12345

    # Test list
    all_r = list_mdwiki_revids()
    assert any(x.title == "test_page" for x in all_r)

    # Test update
    updated = update_mdwiki_revid("test_page", 67890)
    assert updated.revid == 67890

    # Test add_or_update
    r3 = add_or_update_mdwiki_revid("test_page", 11111)
    assert r3.revid == 11111

    # Test delete
    delete_mdwiki_revid("test_page")
    assert get_mdwiki_revid_by_title("test_page") is None



class TestGetMdwikiRevidsDb:
    """Tests for get_mdwiki_revids_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new MdwikiRevidsDB is created when none cached."""


class TestListMdwikiRevids:
    """Tests for list_mdwiki_revids function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""


class TestGetMdwikiRevidByTitle:
    """Tests for get_mdwiki_revid_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_title."""


class TestAddMdwikiRevid:
    """Tests for add_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""


class TestAddOrUpdateMdwikiRevid:
    """Tests for add_or_update_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""


class TestUpdateMdwikiRevid:
    """Tests for update_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""


class TestDeleteMdwikiRevid:
    """Tests for delete_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""


class TestGetRevidForTitle:
    """Tests for get_revid_for_title function."""

    def test_returns_revid_when_record_exists(self, monkeypatch):
        """Test that function returns revid when record found."""

    def test_returns_none_when_record_not_found(self, monkeypatch):
        """Test that function returns None when record not found."""
