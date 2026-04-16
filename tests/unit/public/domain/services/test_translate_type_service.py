"""
Unit tests for domain/services/translate_type_service.py module.

Tests for translate_type service layer which provides cached access to TranslateTypeDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.translate_type_service import (
    add_or_update_translate_type,
    add_translate_type,
    can_translate_full,
    can_translate_lead,
    delete_translate_type,
    get_translate_type,
    get_translate_type_by_title,
    get_translate_type_db,
    list_full_enabled_types,
    list_lead_enabled_types,
    list_translate_types,
    update_translate_type,
)


class TestGetTranslateTypeDb:
    """Tests for get_translate_type_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.services.translate_type_service._TRANSLATE_TYPE_STORE", mock_db)
        monkeypatch.setattr("src.app_main.public.domain.services.translate_type_service.has_db_config", lambda: True)

        result = get_translate_type_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr("src.app_main.public.domain.services.translate_type_service._TRANSLATE_TYPE_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.translate_type_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="TranslateTypeDB requires database configuration"):
            get_translate_type_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new TranslateTypeDB is created when none cached."""
        monkeypatch.setattr("src.app_main.public.domain.services.translate_type_service._TRANSLATE_TYPE_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.translate_type_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.translate_type_service.TranslateTypeDB") as MockDB:
            MockDB.return_value = mock_db_instance

            result = get_translate_type_db()

            assert result is mock_db_instance


class TestListTranslateTypes:
    """Tests for list_translate_types function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = list_translate_types()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestListLeadEnabledTypes:
    """Tests for list_lead_enabled_types function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock()]
        mock_store.list_lead_enabled.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = list_lead_enabled_types()

        assert result is mock_records
        mock_store.list_lead_enabled.assert_called_once()


class TestListFullEnabledTypes:
    """Tests for list_full_enabled_types function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock()]
        mock_store.list_full_enabled.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = list_full_enabled_types()

        assert result is mock_records
        mock_store.list_full_enabled.assert_called_once()


class TestGetTranslateType:
    """Tests for get_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = get_translate_type(123)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(123)


class TestGetTranslateTypeByTitle:
    """Tests for get_translate_type_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_title."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = get_translate_type_by_title("Lead")

        assert result is mock_record
        mock_store.fetch_by_title.assert_called_once_with("Lead")


class TestAddTranslateType:
    """Tests for add_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = add_translate_type("Lead", tt_lead=1, tt_full=0)

        assert result is mock_record
        mock_store.add.assert_called_once_with("Lead", 1, 0)


class TestAddOrUpdateTranslateType:
    """Tests for add_or_update_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add_or_update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = add_or_update_translate_type("Lead", tt_lead=1, tt_full=1)

        assert result is mock_record
        mock_store.add_or_update.assert_called_once_with("Lead", 1, 1)


class TestUpdateTranslateType:
    """Tests for update_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = update_translate_type(1, tt_full=1)

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, tt_full=1)


class TestDeleteTranslateType:
    """Tests for delete_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = delete_translate_type(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)


class TestCanTranslateLead:
    """Tests for can_translate_lead function."""

    def test_returns_true_when_tt_lead_is_1(self, monkeypatch):
        """Test that function returns True when tt_lead is 1."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.tt_lead = 1
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = can_translate_lead("Lead")

        assert result is True

    def test_returns_false_when_tt_lead_is_0(self, monkeypatch):
        """Test that function returns False when tt_lead is 0."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.tt_lead = 0
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = can_translate_lead("Lead")

        assert result is False

    def test_returns_true_when_no_record(self, monkeypatch):
        """Test that function returns True when no record found (default behavior)."""
        mock_store = MagicMock()
        mock_store.fetch_by_title.return_value = None
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = can_translate_lead("Missing")

        assert result is True


class TestCanTranslateFull:
    """Tests for can_translate_full function."""

    def test_returns_true_when_tt_full_is_1(self, monkeypatch):
        """Test that function returns True when tt_full is 1."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.tt_full = 1
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = can_translate_full("Full")

        assert result is True

    def test_returns_false_when_tt_full_is_0(self, monkeypatch):
        """Test that function returns False when tt_full is 0."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.tt_full = 0
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = can_translate_full("Full")

        assert result is False

    def test_returns_false_when_no_record(self, monkeypatch):
        """Test that function returns False when no record found (default behavior)."""
        mock_store = MagicMock()
        mock_store.fetch_by_title.return_value = None
        monkeypatch.setattr(
            "src.app_main.public.domain.services.translate_type_service.get_translate_type_db", lambda: mock_store
        )

        result = can_translate_full("Missing")

        assert result is False
