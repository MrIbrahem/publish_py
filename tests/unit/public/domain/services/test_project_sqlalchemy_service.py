from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.domain_models import ProjectRecord
from src.sqlalchemy_app.public.domain.models import _ProjectRecord
from src.sqlalchemy_app.public.domain.services.project_service import (
    add_or_update_project,
    add_project,
    delete_project,
    get_project,
    get_project_by_title,
    list_projects,
    update_project,
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


def test_project_workflow():
    # Test add
    p = add_project("test_project")
    assert p.g_title == "test_project"

    # Test get
    p2 = get_project(p.g_id)
    assert p2.g_title == "test_project"

    # Test get by title
    p3 = get_project_by_title("test_project")
    assert p3.g_id == p.g_id

    # Test list
    all_p = list_projects()
    assert any(x.g_title == "test_project" for x in all_p)

    # Test update
    updated = update_project(p.g_id, g_title="new_title")
    assert updated.g_title == "new_title"

    # Test add_or_update
    p4 = add_or_update_project("new_title")
    assert p4.g_id == p.g_id

    # Test delete
    delete_project(p.g_id)
    assert get_project(p.g_id) is None


class TestListProjects:
    """Tests for list_projects function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_project("p1")
        add_project("p2")
        result = list_projects()
        assert len(result) >= 2


class TestGetProject:
    """Tests for get_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        p = add_project("p1")
        result = get_project(p.g_id)
        assert isinstance(result, ProjectRecord)
        assert result.g_title == "p1"


class TestGetProjectByTitle:
    """Tests for get_project_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title."""
        add_project("p1")
        result = get_project_by_title("p1")
        assert result.g_title == "p1"


class TestAddProject:
    """Tests for add_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_project("p1")
        assert record.g_title == "p1"


class TestAddOrUpdateProject:
    """Tests for add_or_update_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        p = add_project("p1")
        record = add_or_update_project("p1")
        assert record.g_id == p.g_id
        assert len(list_projects()) == 1


class TestUpdateProject:
    """Tests for update_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        p = add_project("p1")
        updated = update_project(p.g_id, g_title="p2")
        assert updated.g_title == "p2"


class TestDeleteProject:
    """Tests for delete_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        p = add_project("p1")
        delete_project(p.g_id)
        assert get_project(p.g_id) is None
