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
    p = add_project("WikiProject Medicine")
    assert p.g_title == "WikiProject Medicine"

    # Test get
    p2 = get_project(p.g_id)
    assert p2.g_title == "WikiProject Medicine"

    # Test get by title
    p3 = get_project_by_title("WikiProject Medicine")
    assert p3.g_id == p.g_id

    # Test list
    all_p = list_projects()
    assert any(x.g_title == "WikiProject Medicine" for x in all_p)

    # Test update
    updated = update_project(p.g_id, g_title="WP:MED")
    assert updated.g_title == "WP:MED"

    # Test add_or_update
    p4 = add_or_update_project("WP:MED")
    assert p4.g_id == p.g_id

    # Test delete
    delete_project(p.g_id)
    assert get_project(p.g_id) is None


class TestListProjects:
    """Tests for list_projects function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_project("WikiProject History")
        add_project("WikiProject Science")
        result = list_projects()
        assert len(result) >= 2


class TestGetProject:
    """Tests for get_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        p = add_project("WikiProject Anatomy")
        result = get_project(p.g_id)
        assert isinstance(result, ProjectRecord)
        assert result.g_title == "WikiProject Anatomy"


class TestGetProjectByTitle:
    """Tests for get_project_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title."""
        add_project("WikiProject Physiology")
        result = get_project_by_title("WikiProject Physiology")
        assert result.g_title == "WikiProject Physiology"


class TestAddProject:
    """Tests for add_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_project("WikiProject Pharmacology")
        assert record.g_title == "WikiProject Pharmacology"


class TestAddOrUpdateProject:
    """Tests for add_or_update_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        p = add_project("WikiProject Health")
        record = add_or_update_project("WikiProject Health")
        assert record.g_id == p.g_id
        assert len(list_projects()) == 1


class TestUpdateProject:
    """Tests for update_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        p = add_project("WikiProject Genetics")
        updated = update_project(p.g_id, g_title="WP:GENETICS")
        assert updated.g_title == "WP:GENETICS"


class TestDeleteProject:
    """Tests for delete_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        p = add_project("WikiProject Temporary")
        delete_project(p.g_id)
        assert get_project(p.g_id) is None
