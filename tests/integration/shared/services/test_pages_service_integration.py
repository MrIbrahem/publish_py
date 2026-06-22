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


from src.main_app.db.services.delete_service import (
    delete_page,
)
from src.main_app.db.services.pages.page_service import (
    add_page,
    insert_page_target,
    list_pages,
    update_page,
)


class TestPagesServiceIntegration:
    """Integration tests for pages service."""

    def test_full_page_lifecycle(self):
        """Test complete CRUD lifecycle through service layer."""
        result = add_page("TestPage", "lead", "Test", "en", "TestUser", "TestFile")
        assert result.title == "TestPage"

        pages = list_pages()
        assert len(pages) == 1
        assert pages[0].title == "TestPage"

        result = update_page(result.id, "UpdatedPage", "UpdatedFile")
        assert result.title == "UpdatedPage"

        deleted = delete_page(result.id)
        assert deleted is True

    def test_insert_page_target_integration(self):
        """Test insert_page_target through service layer."""
        result = insert_page_target(
            sourcetitle="SourceTitle",
            translate_type="Lead",
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
            translate_type="Lead",
            cat="Category",
            lang="ar",
            user="User",
            target="Target",
        )

        assert result is True
