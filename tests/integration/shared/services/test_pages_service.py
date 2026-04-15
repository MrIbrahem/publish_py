"""Integration tests for pages_service module.

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
from src.app_main.shared.services.pages_service import (
    add_or_update_page,
    add_page,
    delete_page,
    find_exists_or_update,
    get_pages_db,
    insert_page_target,
    list_pages,
    update_page,
)


class TestPagesServiceIntegration:
    """Integration tests for pages service."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self, monkeypatch):
        """Reset the singleton before each test."""
        monkeypatch.setattr("src.app_main.shared.services.pages_service._PAGE_STORE", None)

    def test_full_page_lifecycle(self, monkeypatch):
        """Test complete CRUD lifecycle through service layer."""
        mock_db = MagicMock()
        mock_record = MagicMock()
        mock_record.id = 1
        mock_record.title = "TestPage"

        with patch("src.app_main.shared.services.pages_service.PagesDB") as MockPagesDB:
            MockPagesDB.return_value = mock_db
            monkeypatch.setattr("src.app_main.shared.services.pages_service.has_db_config", lambda: True)

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

    def test_service_reuses_db_instance(self, monkeypatch):
        """Test that service reuses DB instance across operations."""
        mock_db = MagicMock()

        with patch("src.app_main.shared.services.pages_service.PagesDB") as MockPagesDB:
            MockPagesDB.return_value = mock_db
            monkeypatch.setattr("src.app_main.shared.services.pages_service.has_db_config", lambda: True)

            # Multiple operations
            list_pages()
            add_page("Page1", "File1")
            update_page(1, "Page2", "File2")

            # PagesDB should only be instantiated once (singleton pattern)
            MockPagesDB.assert_called_once()

    def test_add_or_update_integration(self, monkeypatch):
        """Test add_or_update through service layer."""
        mock_db = MagicMock()
        mock_record = MagicMock()

        with patch("src.app_main.shared.services.pages_service.PagesDB") as MockPagesDB:
            MockPagesDB.return_value = mock_db
            monkeypatch.setattr("src.app_main.shared.services.pages_service.has_db_config", lambda: True)

            mock_db.add_or_update.return_value = mock_record

            result = add_or_update_page("TestPage", "TestFile")

            assert result is mock_record
            mock_db.add_or_update.assert_called_once_with("TestPage", "TestFile")

    def test_find_exists_or_update_integration(self, monkeypatch):
        """Test find_exists_or_update through service layer."""
        mock_db = MagicMock()

        with patch("src.app_main.shared.services.pages_service.PagesDB") as MockPagesDB:
            MockPagesDB.return_value = mock_db
            monkeypatch.setattr("src.app_main.shared.services.pages_service.has_db_config", lambda: True)

            # Test when record exists
            mock_db._find_exists_or_update.return_value = True
            result = find_exists_or_update("TestTitle", "ar", "TestUser", "Target", False)
            assert result is True

            # Test when record doesn't exist
            mock_db._find_exists_or_update.return_value = False
            result = find_exists_or_update("NewTitle", "ar", "TestUser", "Target", False)
            assert result is False

    def test_insert_page_target_integration(self, monkeypatch):
        """Test insert_page_target through service layer."""
        mock_db = MagicMock()

        with patch("src.app_main.shared.services.pages_service.PagesDB") as MockPagesDB:
            MockPagesDB.return_value = mock_db
            monkeypatch.setattr("src.app_main.shared.services.pages_service.has_db_config", lambda: True)

            mock_db.insert_page_target.return_value = True

            result = insert_page_target(
                sourcetitle="SourceTitle",
                tr_type="Lead",
                cat="Category:Health",
                lang="ar",
                user="TestUser",
                target="TargetTitle",
                table_name="pages",
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

    def test_handles_db_initialization_failure(self, monkeypatch):
        """Test service handles DB initialization failure."""
        monkeypatch.setattr("src.app_main.shared.services.pages_service._PAGE_STORE", None)
        monkeypatch.setattr("src.app_main.shared.services.pages_service.has_db_config", lambda: True)

        with patch("src.app_main.shared.services.pages_service.PagesDB") as MockPagesDB:
            MockPagesDB.side_effect = Exception("DB Connection Failed")

            with pytest.raises(RuntimeError, match="Unable to initialize page store"):
                get_pages_db()

    def test_validates_config_before_db_access(self, monkeypatch):
        """Test service validates config before attempting DB operations."""
        monkeypatch.setattr("src.app_main.shared.services.pages_service._PAGE_STORE", None)
        monkeypatch.setattr("src.app_main.shared.services.pages_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="PagesDB requires database configuration"):
            get_pages_db()

    def test_insert_page_target_error_propagation(self, monkeypatch):
        """Test that errors from DB are returned through service."""
        mock_db = MagicMock()

        with patch("src.app_main.shared.services.pages_service.PagesDB") as MockPagesDB:
            MockPagesDB.return_value = mock_db
            monkeypatch.setattr("src.app_main.shared.services.pages_service.has_db_config", lambda: True)

            # Simulate error from DB
            mock_db.insert_page_target.return_value = "Error: Duplicate entry"

            result = insert_page_target(
                sourcetitle="Source",
                tr_type="Lead",
                cat="Category",
                lang="ar",
                user="User",
                target="Target",
                table_name="pages",
            )

            # Error message should be passed through
            assert "Error" in result
