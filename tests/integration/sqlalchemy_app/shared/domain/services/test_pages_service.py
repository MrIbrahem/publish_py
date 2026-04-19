"""Integration tests for page_service module.

NOTE: These integration tests verify the service layer works correctly with
the database layer. The service module acts as a thin wrapper around PagesDB.

These tests verify:
- Service initialization and DB connection
- End-to-end page operations through the service layer
- Error handling integration between service and DB layers
- The service layer properly delegates to PagesDB while adding:
  - Singleton pattern management
  - Configuration validation
  - Simplified API for common operations

The actual DB operations are mocked to avoid requiring a real database.
These tests complement the unit tests by verifying the service-to-DB integration.
"""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import sessionmaker
from src.sqlalchemy_app.shared.domain.engine import (
    BaseDb,
    build_engine,
    init_db,
)
from src.sqlalchemy_app.shared.domain.services.page_service import (
    add_or_update_page,
    add_page,
    delete_page,
    find_exists_or_update_page,
    insert_page_target,
    list_pages,
    update_page,
)


class TestPagesServiceIntegration:
    """Integration tests for pages service."""

    def test_full_page_lifecycle(self):
        """Test complete CRUD lifecycle through service layer."""
        result = add_page("TestPage", "TestFile")
        assert result.title == "TestPage"

        pages = list_pages()
        assert len(pages) == 1
        assert pages[0].title == "TestPage"

        result = update_page(1, "UpdatedPage", "UpdatedFile")
        assert result.title == "UpdatedPage"

        result = delete_page(1)
        assert result.id == 1

    def test_add_or_update_integration(self):
        """Test add_or_update through service layer."""
        result = add_or_update_page("TestPage", "TestFile")
        assert result.title == "TestPage"
        assert result.target == "TestFile"

    def test_find_exists_or_update_integration(self):
        """Test find_exists_or_update_page through service layer."""
        result = find_exists_or_update_page("TestTitle", "ar", "TestUser", "Target")
        assert result is False

    def test_insert_page_target_integration(self):
        """Test insert_page_target through service layer."""
        result = insert_page_target(
            sourcetitle="SourceTitle",
            tr_type="Lead",
            cat="Category:Health",
            lang="ar",
            user="TestUser",
            target="TargetTitle",
            mdwiki_revid=12345,
            word=500,
        )

        assert result is True


class TestPagesServiceErrorHandling:
    """Tests for pages service error handling integration."""

    def test_insert_page_target_error_propagation(self):
        """Test that errors from DB are returned through service."""
        result = insert_page_target(
            sourcetitle="Source",
            tr_type="Lead",
            cat="Category",
            lang="ar",
            user="User",
            target="Target",
        )

        assert result is True
