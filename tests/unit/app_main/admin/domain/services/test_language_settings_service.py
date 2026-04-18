"""
Unit tests for language_settings_service module.
"""

from unittest.mock import MagicMock

import pytest
from src.app_main.admin.domain.services.language_settings_service import (
    add_language_setting,
    add_or_update_language_setting,
    delete_language_setting,
    get_language_setting,
    get_language_setting_by_code,
    get_language_settings_db,
    list_language_settings,
    update_language_setting,
)


class TestGetLanguageSettingsDb:
    """Tests for get_language_settings_db function."""

    def test_returns_cached_instance_on_subsequent_calls(self, monkeypatch):
        """Test that the same instance is returned on multiple calls."""
        mock_store = MagicMock()
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.language_settings_service._LANGUAGE_SETTINGS_STORE", mock_store
        )

        result1 = get_language_settings_db()
        result2 = get_language_settings_db()

        assert result1 is result2

    def test_raises_error_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when database config is missing."""
        monkeypatch.setattr("src.app_main.admin.domain.services.language_settings_service.has_db_config", lambda: False)
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.language_settings_service._LANGUAGE_SETTINGS_STORE", None
        )

        with pytest.raises(RuntimeError, match="LanguageSettingsDB requires database configuration"):
            get_language_settings_db()


class TestListLanguageSettings:
    """Tests for list_language_settings function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_language_settings returns all records."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.language_settings_service.get_language_settings_db", lambda: mock_store
        )

        result = list_language_settings()

        assert result == mock_records


class TestGetLanguageSetting:
    """Tests for get_language_setting function."""

    def test_returns_setting_record(self, monkeypatch):
        """Test that function returns a LanguageSettingRecord."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.language_settings_service.get_language_settings_db", lambda: mock_store
        )

        result = get_language_setting(1)

        assert result is mock_record


class TestGetLanguageSettingByCode:
    """Tests for get_language_setting_by_code function."""

    def test_returns_setting_by_lang_code(self, monkeypatch):
        """Test that function returns setting by language code."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_lang_code.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.language_settings_service.get_language_settings_db", lambda: mock_store
        )

        result = get_language_setting_by_code("ar")

        assert result is mock_record
        mock_store.fetch_by_lang_code.assert_called_once_with("ar")


class TestAddLanguageSetting:
    """Tests for add_language_setting function."""

    def test_adds_setting_and_returns_record(self, monkeypatch):
        """Test that add_language_setting adds and returns the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.language_settings_service.get_language_settings_db", lambda: mock_store
        )

        result = add_language_setting("fr", 1, 0, 1, 0)

        mock_store.add.assert_called_once_with("fr", 1, 0, 1, 0)
        assert result is mock_record


class TestAddOrUpdateLanguageSetting:
    """Tests for add_or_update_language_setting function."""

    def test_upserts_setting(self, monkeypatch):
        """Test that add_or_update_language_setting upserts the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.language_settings_service.get_language_settings_db", lambda: mock_store
        )

        result = add_or_update_language_setting("de", 0, 1, 0, 1)

        mock_store.add_or_update.assert_called_once_with("de", 0, 1, 0, 1)
        assert result is mock_record


class TestUpdateLanguageSetting:
    """Tests for update_language_setting function."""

    def test_updates_setting_and_returns_record(self, monkeypatch):
        """Test that update_language_setting updates and returns the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.language_settings_service.get_language_settings_db", lambda: mock_store
        )

        result = update_language_setting(1, move_dots=1, expend=1)

        mock_store.update.assert_called_once_with(1, move_dots=1, expend=1)
        assert result is mock_record


class TestDeleteLanguageSetting:
    """Tests for delete_language_setting function."""

    def test_deletes_setting(self, monkeypatch):
        """Test that delete_language_setting calls store delete."""
        mock_store = MagicMock()
        monkeypatch.setattr(
            "src.app_main.admin.domain.services.language_settings_service.get_language_settings_db", lambda: mock_store
        )

        delete_language_setting(1)

        mock_store.delete.assert_called_once_with(1)
