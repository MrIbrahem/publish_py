"""
Unit tests for domain/services/views_new_service.py module.

Tests for views_new service layer which provides cached access to ViewsNewDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.views_new_service import (
    add_or_update_views_new,
    add_views_new,
    delete_views_new,
    get_total_views_for_target,
    get_views_by_target_lang_year,
    get_views_new,
    get_views_new_db,
    list_views_by_lang,
    list_views_by_target,
    list_views_new,
    update_views_new,
)


class TestGetViewsNewDb:
    """Tests for get_views_new_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.services.views_new_service._VIEWS_NEW_STORE", mock_db)
        monkeypatch.setattr("src.app_main.public.domain.services.views_new_service.has_db_config", lambda: True)

        result = get_views_new_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr("src.app_main.public.domain.services.views_new_service._VIEWS_NEW_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.views_new_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="ViewsNewDB requires database configuration"):
            get_views_new_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new ViewsNewDB is created when none cached."""
        monkeypatch.setattr("src.app_main.public.domain.services.views_new_service._VIEWS_NEW_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.views_new_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.views_new_service.ViewsNewDB") as MockDB:
            MockDB.return_value = mock_db_instance

            result = get_views_new_db()

            assert result is mock_db_instance


class TestListViewsNew:
    """Tests for list_views_new function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.views_new_service.get_views_new_db", lambda: mock_store
        )

        result = list_views_new()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestListViewsByTarget:
    """Tests for list_views_by_target function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_records = [MagicMock()]
        mock_store.list_by_target.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.views_new_service.get_views_new_db", lambda: mock_store
        )

        result = list_views_by_target("TestPage")

        assert result is mock_records
        mock_store.list_by_target.assert_called_once_with("TestPage")


class TestListViewsByLang:
    """Tests for list_views_by_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_records = [MagicMock()]
        mock_store.list_by_lang.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.views_new_service.get_views_new_db", lambda: mock_store
        )

        result = list_views_by_lang("ar")

        assert result is mock_records
        mock_store.list_by_lang.assert_called_once_with("ar")


class TestGetViewsNew:
    """Tests for get_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.views_new_service.get_views_new_db", lambda: mock_store
        )

        result = get_views_new(123)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(123)


class TestGetViewsByTargetLangYear:
    """Tests for get_views_by_target_lang_year function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_target_lang_year.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.views_new_service.get_views_new_db", lambda: mock_store
        )

        result = get_views_by_target_lang_year("TestPage", "ar", 2024)

        assert result is mock_record
        mock_store.fetch_by_target_lang_year.assert_called_once_with("TestPage", "ar", 2024)


class TestAddViewsNew:
    """Tests for add_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.views_new_service.get_views_new_db", lambda: mock_store
        )

        result = add_views_new("TestPage", "ar", 2024, views=1000)

        assert result is mock_record
        mock_store.add.assert_called_once_with("TestPage", "ar", 2024, 1000)


class TestAddOrUpdateViewsNew:
    """Tests for add_or_update_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.views_new_service.get_views_new_db", lambda: mock_store
        )

        result = add_or_update_views_new("TestPage", "ar", 2024, views=2000)

        assert result is mock_record
        mock_store.add_or_update.assert_called_once_with("TestPage", "ar", 2024, 2000)


class TestUpdateViewsNew:
    """Tests for update_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.views_new_service.get_views_new_db", lambda: mock_store
        )

        result = update_views_new(1, views=2000)

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, views=2000)


class TestDeleteViewsNew:
    """Tests for delete_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.views_new_service.get_views_new_db", lambda: mock_store
        )

        result = delete_views_new(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)


class TestGetTotalViewsForTarget:
    """Tests for get_total_views_for_target function."""

    def test_returns_sum_of_views(self, monkeypatch):
        """Test that function returns sum of views."""
        mock_store = MagicMock()
        mock_record1 = MagicMock()
        mock_record1.views = 1000
        mock_record2 = MagicMock()
        mock_record2.views = 2000
        mock_store.list_by_target.return_value = [mock_record1, mock_record2]
        monkeypatch.setattr(
            "src.app_main.public.domain.services.views_new_service.get_views_new_db", lambda: mock_store
        )

        result = get_total_views_for_target("TestPage")

        assert result == 3000

    def test_returns_zero_when_no_records(self, monkeypatch):
        """Test that function returns 0 when no records."""
        mock_store = MagicMock()
        mock_store.list_by_target.return_value = []
        monkeypatch.setattr(
            "src.app_main.public.domain.services.views_new_service.get_views_new_db", lambda: mock_store
        )

        result = get_total_views_for_target("Missing")

        assert result == 0

    def test_handles_none_views(self, monkeypatch):
        """Test that function handles None views."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.views = None
        mock_store.list_by_target.return_value = [mock_record]
        monkeypatch.setattr(
            "src.app_main.public.domain.services.views_new_service.get_views_new_db", lambda: mock_store
        )

        result = get_total_views_for_target("TestPage")

        assert result == 0
