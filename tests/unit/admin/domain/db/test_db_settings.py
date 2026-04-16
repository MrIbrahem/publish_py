"""
Unit tests for db.db_settings module.

Tests for Settings database operations.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import pymysql
from src.app_main.config import DbConfig
from src.app_main.admin.domain.db.db_settings import SettingsDB
from src.app_main.admin.domain.models.setting import SettingRecord





class TestSettingsDB:
    """Tests for SettingsDB class."""

    def test_fetch_by_id_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns record when ID exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "title": "test_setting", "displayed": "Test Setting", "Type": "check", "value": 1, "ignored": 0}
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.fetch_by_id(1)

        assert isinstance(result, SettingRecord)
        assert result.id == 1
        assert result.title == "test_setting"

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when ID not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_title_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_title returns record when title exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "title": "my_setting", "displayed": "My Setting", "Type": "text", "value": 0, "ignored": 0}
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.fetch_by_title("my_setting")

        assert isinstance(result, SettingRecord)
        assert result.title == "my_setting"

    def test_list_returns_all_records(self, monkeypatch, db_config):
        """Test that list returns all setting records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "title": "setting1", "displayed": "Setting 1", "Type": "check", "value": 1, "ignored": 0},
            {"id": 2, "title": "setting2", "displayed": "Setting 2", "Type": "text", "value": 0, "ignored": 1},
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.list()

        assert len(result) == 2
        assert all(isinstance(r, SettingRecord) for r in result)

    def test_list_active_returns_non_ignored_records(self, monkeypatch, db_config):
        """Test that list_active returns only non-ignored records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "title": "active_setting", "displayed": "Active", "Type": "check", "value": 1, "ignored": 0},
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.list_active()

        assert len(result) == 1
        assert result[0].ignored == 0

    def test_add_inserts_new_record(self, monkeypatch, db_config):
        """Test that add inserts a new setting record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "title": "new_setting", "displayed": "New Setting", "Type": "check", "value": 0, "ignored": 0}
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.add("new_setting", "New Setting", "check", 0, 0)

        assert isinstance(result, SettingRecord)
        assert result.title == "new_setting"

    def test_add_raises_error_when_title_empty(self, monkeypatch, db_config):
        """Test that add raises ValueError when title is empty."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        with pytest.raises(ValueError, match="Title is required"):
            settings_db.add("", "Displayed")

    def test_update_modifies_record(self, monkeypatch, db_config):
        """Test that update modifies a setting record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.side_effect = [
            [{"id": 1, "title": "old", "displayed": "Old", "Type": "check", "value": 0, "ignored": 0}],
            [{"id": 1, "title": "new", "displayed": "New", "Type": "text", "value": 1, "ignored": 1}],
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.update(1, title="new", displayed="New", Type="text", value=1, ignored=1)

        assert isinstance(result, SettingRecord)
        assert result.title == "new"

    def test_delete_removes_record(self, monkeypatch, db_config):
        """Test that delete removes a setting record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "title": "test", "displayed": "Test", "Type": "check", "value": 0, "ignored": 0}
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.delete(1)

        assert isinstance(result, SettingRecord)

    def test_add_or_update_upserts_record(self, monkeypatch, db_config):
        """Test that add_or_update upserts a setting record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "title": "upserted", "displayed": "Upserted", "Type": "check", "value": 1, "ignored": 0}
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.add_or_update("upserted", "Upserted", "check", 1, 0)

        assert isinstance(result, SettingRecord)
        assert result.title == "upserted"
