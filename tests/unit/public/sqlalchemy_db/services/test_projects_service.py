"""
Unit tests for domain/services/project_service.py module.

Tests for projects service layer which provides cached access to ProjectsDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.project_service import (
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

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new ProjectsDB is created when none cached."""


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
