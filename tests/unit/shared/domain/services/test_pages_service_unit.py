"""Unit tests for pages_service module.

NOTE: These tests cover the service layer which acts as a thin wrapper around
the PagesDB class. The actual database operations are thoroughly tested in
test_db_pages.py. These tests focus on:

- Singleton pattern (global _PAGE_STORE caching)
- Error handling when database configuration is missing
- Delegation to underlying PagesDB methods
- Service layer convenience functions

The service layer provides:
- Lazy initialization of PagesDB with caching
- Configuration validation before DB operations
- Simplified API for common page operations
- Mirrors the PHP helper functions from php_src/bots/sql/db_pages.php
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.shared.domain.services.pages_service import (
    add_or_update_page,
    add_page,
    delete_page,
    find_exists_or_update,
    get_pages_db,
    insert_page_target,
    list_pages,
    update_page,
)


class TestGetPagesDb:
    """Tests for get_pages_db function."""

    def test_returns_cached_instance_on_subsequent_calls(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service._PAGE_STORE", mock_db)
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.has_db_config", lambda: True)

        result = get_pages_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service._PAGE_STORE", None)
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="PagesDB requires database configuration"):
            get_pages_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new PagesDB is created when none cached."""
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service._PAGE_STORE", None)
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.shared.domain.services.pages_service.PagesDB") as MockPagesDB:
            MockPagesDB.return_value = mock_db_instance

            result = get_pages_db()

            assert result is mock_db_instance
            MockPagesDB.assert_called_once()

    def test_caches_instance_after_first_creation(self, monkeypatch):
        """Test that created instance is cached for reuse."""
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service._PAGE_STORE", None)
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.shared.domain.services.pages_service.PagesDB") as MockPagesDB:
            MockPagesDB.return_value = mock_db_instance

            # First call
            result1 = get_pages_db()
            # Second call should return cached instance
            result2 = get_pages_db()

            assert result1 is result2 is mock_db_instance
            # PagesDB should only be instantiated once
            MockPagesDB.assert_called_once()


class TestListPages:
    """Tests for list_pages function."""

    def test_returns_list_of_pages(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.get_pages_db", lambda: mock_store)

        result = list_pages()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestAddPage:
    """Tests for add_page function."""

    def test_delegates_to_store_add(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.get_pages_db", lambda: mock_store)

        result = add_page("TestTitle", "TestFile")

        assert result is mock_record
        mock_store.add.assert_called_once_with("TestTitle", "TestFile")


class TestAddOrUpdatePage:
    """Tests for add_or_update_page function."""

    def test_delegates_to_store_add_or_update(self, monkeypatch):
        """Test that function delegates to store.add_or_update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.get_pages_db", lambda: mock_store)

        result = add_or_update_page("TestTitle", "TestFile")

        assert result is mock_record
        mock_store.add_or_update.assert_called_once_with("TestTitle", "TestFile")


class TestUpdatePage:
    """Tests for update_page function."""

    def test_delegates_to_store_update(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.get_pages_db", lambda: mock_store)

        result = update_page(1, "TestTitle", "TestFile")

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, "TestTitle", "TestFile")


class TestDeletePage:
    """Tests for delete_page function."""

    def test_delegates_to_store_delete(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.get_pages_db", lambda: mock_store)

        result = delete_page(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)


class TestFindExistsOrUpdate:
    """Tests for find_exists_or_update function."""

    def test_delegates_to_store_find_exists_or_update(self, monkeypatch):
        """Test that function delegates to store._find_exists_or_update."""
        mock_store = MagicMock()
        mock_store._find_exists_or_update.return_value = True
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.get_pages_db", lambda: mock_store)

        result = find_exists_or_update("TestTitle", "ar", "TestUser", "Target")

        assert result is True
        mock_store._find_exists_or_update.assert_called_once_with("TestTitle", "ar", "TestUser", "Target")

    def test_returns_false_when_not_exists(self, monkeypatch):
        """Test that function returns False when record not found."""
        mock_store = MagicMock()
        mock_store._find_exists_or_update.return_value = False
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.get_pages_db", lambda: mock_store)

        result = find_exists_or_update("TestTitle", "ar", "TestUser", "Target")

        assert result is False


class TestInsertPageTarget:
    """Tests for insert_page_target function."""

    def test_delegates_to_store_insert_page_target(self, monkeypatch):
        """Test that function delegates to store.insert_page_target."""
        mock_store = MagicMock()
        mock_store.insert_page_target.return_value = True
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.get_pages_db", lambda: mock_store)

        result = insert_page_target(
            sourcetitle="Source",
            tr_type="Lead",
            cat="Category",
            lang="ar",
            user="TestUser",
            target="Target",
            mdwiki_revid=12345,
            word=100,
        )

        assert result is True
        mock_store.insert_page_target.assert_called_once_with(
            sourcetitle="Source",
            tr_type="Lead",
            cat="Category",
            lang="ar",
            user="TestUser",
            target="Target",
            mdwiki_revid=12345,
            word=100,
        )

    def test_passes_optional_params(self, monkeypatch):
        """Test that optional parameters are passed correctly."""
        mock_store = MagicMock()
        mock_store.insert_page_target.return_value = True
        monkeypatch.setattr("src.app_main.shared.domain.services.pages_service.get_pages_db", lambda: mock_store)

        # Call with minimal required params
        result = insert_page_target(
            sourcetitle="Source",
            tr_type="Lead",
            cat="Category",
            lang="ar",
            user="TestUser",
            target="Target",
        )

        assert result is True
        # Verify default values for optional params
        call_kwargs = mock_store.insert_page_target.call_args.kwargs
        assert call_kwargs["mdwiki_revid"] is None
        assert call_kwargs["word"] == 0
