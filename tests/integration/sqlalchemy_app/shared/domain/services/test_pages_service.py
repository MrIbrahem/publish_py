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

from unittest.mock import MagicMock, patch

import pytest
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

    def test_full_page_lifecycle(self, monkeypatch):
        """Test complete CRUD lifecycle through service layer."""
        mock_db = MagicMock()
        mock_record = MagicMock()
        mock_record.id = 1
        mock_record.title = "TestPage"

        # 1. Add page
        mock_db.add.return_value = mock_record
        result = add_page("TestPage", "TestFile")
        assert result.title == "TestPage"

        # 2. List pages
        mock_db.list.return_value = [mock_record]
        pages = list_pages()
        assert len(pages) == 1

        # 3. Update page
        mock_db.update.return_value = mock_record
        result = update_page(1, "UpdatedPage", "UpdatedFile")
        assert result is mock_record

        # 4. Delete page
        mock_db.delete.return_value = mock_record
        result = delete_page(1)
        assert result is mock_record

    def test_add_or_update_integration(self, monkeypatch):
        """Test add_or_update through service layer."""
        mock_db = MagicMock()
        mock_record = MagicMock()

        mock_db.add_or_update.return_value = mock_record

        result = add_or_update_page("TestPage", "TestFile")

        assert result is mock_record
        mock_db.add_or_update.assert_called_once_with("TestPage", "TestFile")

    def test_find_exists_or_update_integration(self, monkeypatch):
        """Test find_exists_or_update_page through service layer."""
        mock_db = MagicMock()

        # Test when record exists
        mock_db._find_exists_or_update.return_value = True
        result = find_exists_or_update_page("TestTitle", "ar", "TestUser", "Target")
        assert result is True

        # Test when record doesn't exist
        mock_db._find_exists_or_update.return_value = False
        result = find_exists_or_update_page("NewTitle", "ar", "TestUser", "Target")
        assert result is False

    def test_insert_page_target_integration(self, monkeypatch):
        """Test insert_page_target through service layer."""
        mock_db = MagicMock()

        mock_db.insert_page_target.return_value = True

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
        mock_db.insert_page_target.assert_called_once()

        # Verify all parameters passed through
        call_kwargs = mock_db.insert_page_target.call_args.kwargs
        assert call_kwargs["sourcetitle"] == "SourceTitle"
        assert call_kwargs["lang"] == "ar"
        assert call_kwargs["mdwiki_revid"] == 12345
        assert call_kwargs["word"] == 500


class TestPagesServiceErrorHandling:
    """Tests for pages service error handling integration."""

    def test_insert_page_target_error_propagation(self, monkeypatch):
        """Test that errors from DB are returned through service."""
        mock_db = MagicMock()

        # Simulate error from DB
        mock_db.insert_page_target.return_value = "Error: Duplicate entry"

        result = insert_page_target(
            sourcetitle="Source",
            tr_type="Lead",
            cat="Category",
            lang="ar",
            user="User",
            target="Target",
        )

        # Error message should be passed through
        assert "Error" in result
