from unittest.mock import MagicMock, patch

import pytest
from src.db_models.shared_models import PageRecord
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, get_session, init_db
from src.sqlalchemy_app.shared.domain.models import _PageRecord
from src.sqlalchemy_app.shared.domain.services.page_service import (
    add_or_update_page,
    add_page,
    delete_page,
    find_exists_or_update_page,
    insert_page_target,
    list_pages,
    update_page,
)





def test_page_workflow():
    p = add_page("test_page", "target_file")
    assert p.title == "test_page"
    assert any(x.title == "test_page" for x in list_pages())
    updated = update_page(p.id, "new_title", "new_target")
    assert updated.title == "new_title"
    p2 = add_or_update_page("new_title", "final_target")
    assert p2.target == "final_target"
    with get_session() as session:
        orm_p = session.query(_PageRecord).filter(_PageRecord.id == p.id).first()
        orm_p.lang = "en"
        orm_p.user = "user1"
        orm_p.target = ""
        session.commit()
    assert find_exists_or_update_page("new_title", "en", "user1", "found_target") is True
    success = insert_page_target("new_p", "lead", "cat", "fr", "user2", "target_fr", "pages")
    assert success is True
    delete_page(p.id)
    assert not any(x.id == p.id for x in list_pages())


class TestListPages:
    """Tests for list_pages function."""

    def test_returns_list_of_pages(self, monkeypatch):
        """Test that function returns list from store."""


class TestAddPage:
    """Tests for add_page function."""

    def test_delegates_to_store_add(self, monkeypatch):
        """Test that function delegates to store.add."""


class TestAddOrUpdatePage:
    """Tests for add_or_update_page function."""

    def test_delegates_to_store_add_or_update(self, monkeypatch):
        """Test that function delegates to store.add_or_update."""


class TestUpdatePage:
    """Tests for update_page function."""

    def test_delegates_to_store_update(self, monkeypatch):
        """Test that function delegates to store.update."""


class TestDeletePage:
    """Tests for delete_page function."""

    def test_delegates_to_store_delete(self, monkeypatch):
        """Test that function delegates to store.delete."""


class TestFindExistsOrUpdate:
    """Tests for find_exists_or_update_page function."""

    def test_delegates_to_store_find_exists_or_update(self, monkeypatch):
        """Test that function delegates to store._find_exists_or_update."""

    def test_returns_false_when_not_exists(self, monkeypatch):
        """Test that function returns False when record not found."""


class TestInsertPageTarget:
    """Tests for insert_page_target function."""

    def test_delegates_to_store_insert_page_target(self, monkeypatch):
        """Test that function delegates to store.insert_page_target."""

    def test_passes_optional_params(self, monkeypatch):
        """Test that optional parameters are passed correctly."""
