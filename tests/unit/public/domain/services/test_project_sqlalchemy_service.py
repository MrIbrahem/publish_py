from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import ProjectRecord
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


class TestGetProject:
    """Tests for get_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""


class TestGetProjectByTitle:
    """Tests for get_project_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_title."""


class TestAddProject:
    """Tests for add_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""


class TestAddOrUpdateProject:
    """Tests for add_or_update_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add_or_update."""


class TestUpdateProject:
    """Tests for update_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""


class TestDeleteProject:
    """Tests for delete_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
