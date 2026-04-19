"""
Unit tests for domain/services/enwiki_pageview_service.py module.

Tests for enwiki_pageviews service layer which provides cached access to EnwikiPageviewsDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.enwiki_pageview_service import (
    add_enwiki_pageview,
    add_or_update_enwiki_pageview,
    delete_enwiki_pageview,
    get_enwiki_pageview,
    get_enwiki_pageview_by_title,
    get_enwiki_pageviews_db,
    get_top_enwiki_pageviews,
    list_enwiki_pageviews,
    update_enwiki_pageview,
)


class TestGetEnwikiPageviewsDb:
    """Tests for get_enwiki_pageviews_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr(
            "src.app_main.public.domain.services.enwiki_pageview_service._ENWIKI_PAGEVIEWS_STORE", mock_db
        )
        monkeypatch.setattr("src.app_main.public.domain.services.enwiki_pageview_service.has_db_config", lambda: True)

        result = get_enwiki_pageviews_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr(
            "src.app_main.public.domain.services.enwiki_pageview_service._ENWIKI_PAGEVIEWS_STORE", None
        )
        monkeypatch.setattr("src.app_main.public.domain.services.enwiki_pageview_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="EnwikiPageviewsDB requires database configuration"):
            get_enwiki_pageviews_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new EnwikiPageviewsDB is created when none cached."""
        monkeypatch.setattr(
            "src.app_main.public.domain.services.enwiki_pageview_service._ENWIKI_PAGEVIEWS_STORE", None
        )
        monkeypatch.setattr("src.app_main.public.domain.services.enwiki_pageview_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.enwiki_pageview_service.EnwikiPageviewsDB") as MockDB:
            MockDB.return_value = mock_db_instance

            result = get_enwiki_pageviews_db()

            assert result is mock_db_instance


class TestListEnwikiPageviews:
    """Tests for list_enwiki_pageviews function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.enwiki_pageview_service.get_enwiki_pageviews_db", lambda: mock_store
        )

        result = list_enwiki_pageviews()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestGetTopEnwikiPageviews:
    """Tests for get_top_enwiki_pageviews function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.list_by_views."""
        mock_store = MagicMock()
        mock_records = [MagicMock()]
        mock_store.list_by_views.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.enwiki_pageview_service.get_enwiki_pageviews_db", lambda: mock_store
        )

        result = get_top_enwiki_pageviews(limit=50)

        assert result is mock_records
        mock_store.list_by_views.assert_called_once_with(50)

    def test_uses_default_limit(self, monkeypatch):
        """Test that function uses default limit of 100."""
        mock_store = MagicMock()
        mock_store.list_by_views.return_value = []
        monkeypatch.setattr(
            "src.app_main.public.domain.services.enwiki_pageview_service.get_enwiki_pageviews_db", lambda: mock_store
        )

        get_top_enwiki_pageviews()

        mock_store.list_by_views.assert_called_once_with(100)


class TestGetEnwikiPageview:
    """Tests for get_enwiki_pageview function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.enwiki_pageview_service.get_enwiki_pageviews_db", lambda: mock_store
        )

        result = get_enwiki_pageview(123)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(123)


class TestGetEnwikiPageviewByTitle:
    """Tests for get_enwiki_pageview_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_title."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.enwiki_pageview_service.get_enwiki_pageviews_db", lambda: mock_store
        )

        result = get_enwiki_pageview_by_title("TestPage")

        assert result is mock_record
        mock_store.fetch_by_title.assert_called_once_with("TestPage")


class TestAddEnwikiPageview:
    """Tests for add_enwiki_pageview function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.enwiki_pageview_service.get_enwiki_pageviews_db", lambda: mock_store
        )

        result = add_enwiki_pageview("TestPage", en_views=1000)

        assert result is mock_record
        mock_store.add.assert_called_once_with("TestPage", 1000)


class TestAddOrUpdateEnwikiPageview:
    """Tests for add_or_update_enwiki_pageview function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.enwiki_pageview_service.get_enwiki_pageviews_db", lambda: mock_store
        )

        result = add_or_update_enwiki_pageview("TestPage", en_views=2000)

        assert result is mock_record
        mock_store.add_or_update.assert_called_once_with("TestPage", 2000)


class TestUpdateEnwikiPageview:
    """Tests for update_enwiki_pageview function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.enwiki_pageview_service.get_enwiki_pageviews_db", lambda: mock_store
        )

        result = update_enwiki_pageview(1, en_views=2000)

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, en_views=2000)


class TestDeleteEnwikiPageview:
    """Tests for delete_enwiki_pageview function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.enwiki_pageview_service.get_enwiki_pageviews_db", lambda: mock_store
        )

        result = delete_enwiki_pageview(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)
