"""
Unit tests for settings_service module.
"""

from unittest.mock import MagicMock

import pytest
from src.app_main.admin.domain.services.settings_service import (
    add_setting,
    delete_setting,
    get_setting,
    get_settings_db,
    list_settings,
)


class TestGetSettingsDb:
    """Tests for get_settings_db function."""

    def test_returns_cached_instance_on_subsequent_calls(self, monkeypatch):
        """Test that the same instance is returned on multiple calls."""
        mock_store = MagicMock()
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service._SETTINGS_STORE", mock_store)

        result1 = get_settings_db()
        result2 = get_settings_db()

        assert result1 is result2

    def test_raises_error_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when database config is missing."""
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service.has_db_config", lambda: False)
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service._SETTINGS_STORE", None)

        with pytest.raises(RuntimeError, match="SettingsDB requires database configuration"):
            get_settings_db()


class TestListSettings:
    """Tests for list_settings function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_settings returns all records."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service.get_settings_db", lambda: mock_store)

        result = list_settings()

        assert result == mock_records


class TestGetSetting:
    """Tests for get_setting function."""

    def test_returns_setting_record(self, monkeypatch):
        """Test that function returns a SettingRecord."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service.get_settings_db", lambda: mock_store)

        result = get_setting(1)

        assert result is mock_record


class TestAddSetting:
    """Tests for add_setting function."""

    def test_adds_setting_and_returns_record(self, monkeypatch):
        """Test that add_setting adds and returns the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service.get_settings_db", lambda: mock_store)

        result = add_setting("new_setting", "New Setting", "check", 1, 0)

        mock_store.add.assert_called_once_with("new_setting", "New Setting", "check", 1, 0)
        assert result is mock_record


class TestDeleteSetting:
    """Tests for delete_setting function."""

    def test_deletes_setting(self, monkeypatch):
        """Test that delete_setting calls store delete."""
        mock_store = MagicMock()
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service.get_settings_db", lambda: mock_store)

        delete_setting(1)

        mock_store.delete.assert_called_once_with(1)
