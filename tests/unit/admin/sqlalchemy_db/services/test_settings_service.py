"""
Unit tests for setting_service module.
"""

from unittest.mock import MagicMock

import pytest
from src.sqlalchemy_app.admin.domain.services.setting_service import (
    add_setting,
    delete_setting,
    get_setting,
    get_setting_by_key,
    list_settings,
    update_value,
)


class TestGetSettingsDb:
    """Tests for get_settings_db function."""

    def test_returns_cached_instance_on_subsequent_calls(self, monkeypatch):
        """Test that the same instance is returned on multiple calls."""








    def test_raises_error_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when database config is missing."""







class TestListSettings:
    """Tests for list_settings function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_settings returns all records."""










class TestGetSetting:
    """Tests for get_setting function."""

    def test_returns_setting_record(self, monkeypatch):
        """Test that function returns a SettingRecord."""










class TestGetSettingByKey:
    """Tests for get_setting_by_key function."""

    def test_returns_setting_by_key(self, monkeypatch):
        """Test that function returns a SettingRecord by key."""











class TestAddSetting:
    """Tests for add_setting function."""

    def test_adds_setting_and_returns_record(self, monkeypatch):
        """Test that add_setting adds and returns the record."""











class TestUpdateValue:
    """Tests for update_value function."""

    def test_updates_setting_value(self, monkeypatch):
        """Test that update_value updates the setting value."""











class TestDeleteSetting:
    """Tests for delete_setting function."""

    def test_deletes_setting(self, monkeypatch):
        """Test that delete_setting calls store delete."""






