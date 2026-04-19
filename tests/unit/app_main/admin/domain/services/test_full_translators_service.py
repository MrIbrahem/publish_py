"""
Unit tests for full_translator_service module.
"""

from unittest.mock import MagicMock

import pytest
from src.app_main.admin.domain.services.full_translator_service import (
    add_full_translator,
    add_or_update_full_translator,
    delete_full_translator,
    get_full_translator,
    get_full_translator_by_user,
    get_full_translators_db,
    is_full_translator,
    list_active_full_translators,
    list_full_translators,
    update_full_translator,
)


class TestGetFullTranslatorsDb:
    """Tests for get_full_translators_db function."""

    def test_returns_cached_instance_on_subsequent_calls(self, monkeypatch):
        """Test that the same instance is returned on multiple calls."""
        mock_store = MagicMock()
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.full_translator_service._FULL_TRANSLATORS_STORE", mock_store
        )

        result1 = get_full_translators_db()
        result2 = get_full_translators_db()

        assert result1 is result2

    def test_raises_error_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when database config is missing."""
        monkeypatch.setattr("src.app_main.admin.domain.services.full_translator_service.has_db_config", lambda: False)
        monkeypatch.setattr("src.app_main.admin.domain.services.full_translator_service._FULL_TRANSLATORS_STORE", None)

        with pytest.raises(RuntimeError, match="FullTranslatorsDB requires database configuration"):
            get_full_translators_db()


class TestListFullTranslators:
    """Tests for list_full_translators function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_full_translators returns all records."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.full_translator_service.get_full_translators_db", lambda: mock_store
        )

        result = list_full_translators()

        assert result == mock_records


class TestListActiveFullTranslators:
    """Tests for list_active_full_translators function."""

    def test_returns_active_records(self, monkeypatch):
        """Test that list_active_full_translators returns active records."""
        mock_store = MagicMock()
        mock_records = [MagicMock()]
        mock_store.list_active.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.full_translator_service.get_full_translators_db", lambda: mock_store
        )

        result = list_active_full_translators()

        assert result == mock_records


class TestGetFullTranslator:
    """Tests for get_full_translator function."""

    def test_returns_translator_record(self, monkeypatch):
        """Test that function returns a FullTranslatorRecord."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.full_translator_service.get_full_translators_db", lambda: mock_store
        )

        result = get_full_translator(1)

        assert result is mock_record


class TestGetFullTranslatorByUser:
    """Tests for get_full_translator_by_user function."""

    def test_returns_translator_by_user(self, monkeypatch):
        """Test that function returns translator by username."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_user.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.full_translator_service.get_full_translators_db", lambda: mock_store
        )

        result = get_full_translator_by_user("TestUser")

        assert result is mock_record


class TestAddFullTranslator:
    """Tests for add_full_translator function."""

    def test_adds_translator_and_returns_record(self, monkeypatch):
        """Test that add_full_translator adds and returns the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.full_translator_service.get_full_translators_db", lambda: mock_store
        )

        result = add_full_translator("NewUser", 1)

        assert result is mock_record


class TestAddOrUpdateFullTranslator:
    """Tests for add_or_update_full_translator function."""

    def test_upserts_translator(self, monkeypatch):
        """Test that add_or_update_full_translator upserts the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.full_translator_service.get_full_translators_db", lambda: mock_store
        )

        result = add_or_update_full_translator("TestUser", 1)

        assert result is mock_record


class TestUpdateFullTranslator:
    """Tests for update_full_translator function."""

    def test_updates_translator_and_returns_record(self, monkeypatch):
        """Test that update_full_translator updates and returns the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.full_translator_service.get_full_translators_db", lambda: mock_store
        )

        result = update_full_translator(1, user="UpdatedUser")

        assert result is mock_record


class TestDeleteFullTranslator:
    """Tests for delete_full_translator function."""

    def test_deletes_translator(self, monkeypatch):
        """Test that delete_full_translator calls store delete."""
        mock_store = MagicMock()
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.full_translator_service.get_full_translators_db", lambda: mock_store
        )

        delete_full_translator(1)

        mock_store.delete.assert_called_once_with(1)


class TestIsFullTranslator:
    """Tests for is_full_translator function."""

    def test_returns_true_when_user_is_active_translator(self, monkeypatch):
        """Test that is_full_translator returns True for active translator."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.active = 1
        mock_store.fetch_by_user.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.full_translator_service.get_full_translators_db", lambda: mock_store
        )

        result = is_full_translator("TranslatorUser")

        assert result is True

    def test_returns_false_when_user_not_translator(self, monkeypatch):
        """Test that is_full_translator returns False when user not found."""
        mock_store = MagicMock()
        mock_store.fetch_by_user.return_value = None
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.full_translator_service.get_full_translators_db", lambda: mock_store
        )

        result = is_full_translator("RegularUser")

        assert result is False

    def test_returns_false_when_translator_inactive(self, monkeypatch):
        """Test that is_full_translator returns False for inactive translator."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.active = 0
        mock_store.fetch_by_user.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.full_translator_service.get_full_translators_db", lambda: mock_store
        )

        result = is_full_translator("InactiveTranslator")

        assert result is False
