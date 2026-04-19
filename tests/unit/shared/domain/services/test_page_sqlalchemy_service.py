from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.shared.domain_models import PageRecord
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
    success = insert_page_target("new_p", "lead", "cat", "fr", "user2", "target_fr", word=100)
    assert success is True
    delete_page(p.id)
    assert not any(x.id == p.id for x in list_pages())


class TestListPages:
    """Tests for list_pages function."""

    def test_returns_list_of_pages(self, monkeypatch):
        """Test that function returns list from store."""
        add_page("p1", "t1")
        add_page("p2", "t2")
        result = list_pages()
        assert len(result) >= 2
        assert any(p.title == "p1" for p in result)


class TestAddPage:
    """Tests for add_page function."""

    def test_delegates_to_store_add(self, monkeypatch):
        """Test that function adds a page."""
        record = add_page("p1", "t1")
        assert record.title == "p1"
        assert record.target == "t1"


class TestAddOrUpdatePage:
    """Tests for add_or_update_page function."""

    def test_delegates_to_store_add_or_update(self, monkeypatch):
        """Test that function updates if exists."""
        add_page("p1", "t1")
        record = add_or_update_page("p1", "t2")
        assert record.target == "t2"


class TestUpdatePage:
    """Tests for update_page function."""

    def test_delegates_to_store_update(self, monkeypatch):
        """Test that function updates the record."""
        p = add_page("p1", "t1")
        updated = update_page(p.id, "p2", "t2")
        assert updated.title == "p2"
        assert updated.target == "t2"


class TestDeletePage:
    """Tests for delete_page function."""

    def test_delegates_to_store_delete(self, monkeypatch):
        """Test that function deletes the record."""
        p = add_page("p1", "t1")
        delete_page(p.id)
        assert not any(x.id == p.id for x in list_pages())


class TestFindExistsOrUpdate:
    """Tests for find_exists_or_update_page function."""

    def test_delegates_to_store_find_exists_or_update(self, monkeypatch):
        """Test that function updates target if empty."""
        # Manual insert to set specific fields
        with get_session() as session:
            session.add(_PageRecord(title="p1", lang="en", user="u1", target=""))
            session.commit()

        result = find_exists_or_update_page("p1", "en", "u1", "new_t")
        assert result is True

        # Verify update
        pages = list_pages()
        p = next(p for p in pages if p.title == "p1")
        assert p.target == "new_t"

    def test_returns_false_when_not_exists(self, monkeypatch):
        """Test that function returns False when record not found."""
        result = find_exists_or_update_page("non", "en", "u", "t")
        assert result is False


class TestInsertPageTarget:
    """Tests for insert_page_target function."""

    def test_delegates_to_store_insert_page_target(self, monkeypatch):
        """Test that function inserts correctly."""
        success = insert_page_target("s1", "type", "cat", "en", "u1", "target")
        assert success is True
        assert any(p.title == "s1" for p in list_pages())

    def test_passes_optional_params(self, monkeypatch):
        """Test that optional parameters are passed correctly."""
        success = insert_page_target("s2", "type", "cat", "en", "u1", "target", mdwiki_revid=123, word=50)
        assert success is True
        p = next(p for p in list_pages() if p.title == "s2")
        assert p.mdwiki_revid == 123
        assert p.word == 50
