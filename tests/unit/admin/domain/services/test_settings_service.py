"""
Unit tests for settings_service module.
"""

from unittest.mock import MagicMock

import pytest
from src.app_main.admin.domain.services.settings_service import (
    add_or_update_setting,
    add_setting,
    delete_setting,
    get_setting,
    get_setting_by_title,
    get_setting_value,
    get_settings_db,
    list_active_settings,
    list_settings,
    update_setting,
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


class TestListActiveSettings:
    """Tests for list_active_settings function."""

    def test_returns_active_records(self, monkeypatch):
        """Test that list_active_settings returns non-ignored records."""
        mock_store = MagicMock()
        mock_records = [MagicMock()]
        mock_store.list_active.return_value = mock_records
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service.get_settings_db", lambda: mock_store)

        result = list_active_settings()

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


class TestGetSettingByTitle:
    """Tests for get_setting_by_title function."""

    def test_returns_setting_by_title(self, monkeypatch):
        """Test that function returns setting by title."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service.get_settings_db", lambda: mock_store)

        result = get_setting_by_title("my_setting")

        assert result is mock_record
        mock_store.fetch_by_title.assert_called_once_with("my_setting")


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


class TestAddOrUpdateSetting:
    """Tests for add_or_update_setting function."""

    def test_upserts_setting(self, monkeypatch):
        """Test that add_or_update_setting upserts the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service.get_settings_db", lambda: mock_store)

        result = add_or_update_setting("test_setting", "Test Setting", "text", 0, 0)

        mock_store.add_or_update.assert_called_once_with("test_setting", "Test Setting", "text", 0, 0)
        assert result is mock_record


class TestUpdateSetting:
    """Tests for update_setting function."""

    def test_updates_setting_and_returns_record(self, monkeypatch):
        """Test that update_setting updates and returns the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service.get_settings_db", lambda: mock_store)

        result = update_setting(1, value=1, ignored=0)

        mock_store.update.assert_called_once_with(1, value=1, ignored=0)
        assert result is mock_record


class TestDeleteSetting:
    """Tests for delete_setting function."""

    def test_deletes_setting(self, monkeypatch):
        """Test that delete_setting calls store delete."""
        mock_store = MagicMock()
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service.get_settings_db", lambda: mock_store)

        delete_setting(1)

        mock_store.delete.assert_called_once_with(1)


class TestGetSettingValue:
    """Tests for get_setting_value function."""

    def test_returns_setting_value_when_found(self, monkeypatch):
        """Test that get_setting_value returns the value when setting found."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.value = 42
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service.get_settings_db", lambda: mock_store)

        result = get_setting_value("my_setting")

        assert result == 42

    def test_returns_default_when_not_found(self, monkeypatch):
        """Test that get_setting_value returns default when setting not found."""
        mock_store = MagicMock()
        mock_store.fetch_by_title.return_value = None
        monkeypatch.setattr("src.app_main.admin.domain.services.settings_service.get_settings_db", lambda: mock_store)

        result = get_setting_value("missing_setting", default=100)

        assert result == 100
