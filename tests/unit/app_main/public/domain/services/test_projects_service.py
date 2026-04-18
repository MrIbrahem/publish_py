"""
Unit tests for domain/services/projects_service.py module.

Tests for projects service layer which provides cached access to ProjectsDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.projects_service import (
    add_or_update_project,
    add_project,
    delete_project,
    get_project,
    get_project_by_title,
    get_projects_db,
    list_projects,
    update_project,
)


class TestGetProjectsDb:
    """Tests for get_projects_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service._PROJECTS_STORE", mock_db)
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service.has_db_config", lambda: True)

        result = get_projects_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service._PROJECTS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="ProjectsDB requires database configuration"):
            get_projects_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new ProjectsDB is created when none cached."""
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service._PROJECTS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.projects_service.ProjectsDB") as MockDB:
            MockDB.return_value = mock_db_instance

            result = get_projects_db()

            assert result is mock_db_instance


class TestListProjects:
    """Tests for list_projects function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service.get_projects_db", lambda: mock_store)

        result = list_projects()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestGetProject:
    """Tests for get_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service.get_projects_db", lambda: mock_store)

        result = get_project(123)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(123)


class TestGetProjectByTitle:
    """Tests for get_project_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_title."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service.get_projects_db", lambda: mock_store)

        result = get_project_by_title("Wikipedia")

        assert result is mock_record
        mock_store.fetch_by_title.assert_called_once_with("Wikipedia")


class TestAddProject:
    """Tests for add_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service.get_projects_db", lambda: mock_store)

        result = add_project("Wikipedia")

        assert result is mock_record
        mock_store.add.assert_called_once_with("Wikipedia")


class TestAddOrUpdateProject:
    """Tests for add_or_update_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add_or_update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service.get_projects_db", lambda: mock_store)

        result = add_or_update_project("Wikipedia")

        assert result is mock_record
        mock_store.add_or_update.assert_called_once_with("Wikipedia")


class TestUpdateProject:
    """Tests for update_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service.get_projects_db", lambda: mock_store)

        result = update_project(1, g_title="NewTitle")

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, g_title="NewTitle")


class TestDeleteProject:
    """Tests for delete_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.projects_service.get_projects_db", lambda: mock_store)

        result = delete_project(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)
