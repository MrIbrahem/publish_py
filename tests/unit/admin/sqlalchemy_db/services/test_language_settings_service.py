"""
Unit tests for language_setting_service module.
"""

from unittest.mock import MagicMock

import pytest
from src.sqlalchemy_app.admin.domain.services.language_setting_service import (
    add_language_setting,
    add_or_update_language_setting,
    delete_language_setting,
    get_language_setting,
    get_language_setting_by_code,
    list_language_settings,
    update_language_setting,
)


class TestGetLanguageSettingsDb:
    """Tests for get_language_settings_db function."""

    def test_returns_cached_instance_on_subsequent_calls(self, monkeypatch):
        """Test that the same instance is returned on multiple calls."""










    def test_raises_error_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when database config is missing."""









class TestListLanguageSettings:
    """Tests for list_language_settings function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_language_settings returns all records."""












class TestGetLanguageSetting:
    """Tests for get_language_setting function."""

    def test_returns_setting_record(self, monkeypatch):
        """Test that function returns a LanguageSettingRecord."""












class TestGetLanguageSettingByCode:
    """Tests for get_language_setting_by_code function."""

    def test_returns_setting_by_lang_code(self, monkeypatch):
        """Test that function returns setting by language code."""













class TestAddLanguageSetting:
    """Tests for add_language_setting function."""

    def test_adds_setting_and_returns_record(self, monkeypatch):
        """Test that add_language_setting adds and returns the record."""













class TestAddOrUpdateLanguageSetting:
    """Tests for add_or_update_language_setting function."""

    def test_upserts_setting(self, monkeypatch):
        """Test that add_or_update_language_setting upserts the record."""













class TestUpdateLanguageSetting:
    """Tests for update_language_setting function."""

    def test_updates_setting_and_returns_record(self, monkeypatch):
        """Test that update_language_setting updates and returns the record."""













class TestDeleteLanguageSetting:
    """Tests for delete_language_setting function."""

    def test_deletes_setting(self, monkeypatch):
        """Test that delete_language_setting calls store delete."""








