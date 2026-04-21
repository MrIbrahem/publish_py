from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.db_models.public_models import ProjectRecord
from src.sqlalchemy_app.sqlalchemy_models import _ProjectRecord
from src.sqlalchemy_app.public.services.project_service import (
    add_project,
    delete_project,
    get_project,
    get_project_by_title,
    list_projects,
    update_project,
)


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

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_project(9999) is None


class TestGetProjectByTitle:
    """Tests for get_project_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title."""
        add_project("WikiProject Physiology")
        result = get_project_by_title("WikiProject Physiology")
        assert result.g_title == "WikiProject Physiology"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_project_by_title("Ghost") is None


class TestAddProject:
    """Tests for add_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_project("WikiProject Pharmacology")
        assert record.g_title == "WikiProject Pharmacology"

    def test_raises_error_if_exists(self, monkeypatch):
        add_project("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            add_project("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Project title is required"):
            add_project("")


class TestUpdateProject:
    """Tests for update_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        p = add_project("WikiProject Genetics")
        updated = update_project(p.g_id, g_title="WP:GENETICS")
        assert updated.g_title == "WP:GENETICS"

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        p = add_project("No_Change")
        result = update_project(p.g_id)
        assert result.g_title == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_project(9999, g_title="T")


class TestDeleteProject:
    """Tests for delete_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        p = add_project("WikiProject Temporary")
        delete_project(p.g_id)
        assert get_project(p.g_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_project(9999)
