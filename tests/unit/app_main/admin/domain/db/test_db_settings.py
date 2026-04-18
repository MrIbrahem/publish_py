"""
Unit tests for db.db_settings module.

Tests for Settings database operations.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.admin.domain.db.db_settings import SettingsDB
from src.app_main.admin.domain.models import SettingRecord
from src.app_main.config import DbConfig


class TestSettingsDB:
    """Tests for SettingsDB class."""

    def test_fetch_by_id_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns record when ID exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "key": "test_key",
                "title": "Test Setting",
                "value_type": "boolean",
                "value": "true",
            }
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.fetch_by_id(1)

        assert isinstance(result, SettingRecord)
        assert result.id == 1
        assert result.key == "test_key"
        assert result.title == "Test Setting"

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when ID not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_key_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_key returns record when key exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "key": "my_setting",
                "title": "My Setting",
                "value_type": "string",
                "value": "test value",
            }
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.fetch_by_key("my_setting")

        assert isinstance(result, SettingRecord)
        assert result.key == "my_setting"

    def test_fetch_by_key_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_key returns None when key not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.fetch_by_key("nonexistent_key")

        assert result is None

    def test_list_returns_all_records(self, monkeypatch, db_config):
        """Test that list returns all setting records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "key": "setting1",
                "title": "Setting 1",
                "value_type": "boolean",
                "value": "true",
            },
            {
                "id": 2,
                "key": "setting2",
                "title": "Setting 2",
                "value_type": "string",
                "value": "hello",
            },
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.list()

        assert len(result) == 2
        assert all(isinstance(r, SettingRecord) for r in result)

    def test_add_inserts_new_record(self, monkeypatch, db_config):
        """Test that add inserts a new setting record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "key": "new_key",
                "title": "New Setting",
                "value_type": "boolean",
                "value": "false",
            }
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.add("new_key", "New Setting", "boolean", "false")

        assert isinstance(result, SettingRecord)
        assert result.key == "new_key"
        assert result.title == "New Setting"

    def test_add_raises_error_when_key_empty(self, monkeypatch, db_config):
        """Test that add raises ValueError when key is empty."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        with pytest.raises(ValueError, match="Key is required"):
            settings_db.add("", "Title")

    def test_add_raises_error_when_title_empty(self, monkeypatch, db_config):
        """Test that add raises ValueError when title is empty."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        with pytest.raises(ValueError, match="Title is required"):
            settings_db.add("key", "")

    def test_add_raises_error_when_key_already_exists(self, monkeypatch, db_config):
        """Test that add raises ValueError when key already exists."""
        mock_db = MagicMock()
        mock_db.execute_query.side_effect = pymysql.err.IntegrityError("Duplicate entry")

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        with pytest.raises(ValueError, match="already exists"):
            settings_db.add("existing_key", "Title")

    def test_update_value_modifies_record(self, monkeypatch, db_config):
        """Test that update_value modifies a setting record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.side_effect = [
            [
                {
                    "id": 1,
                    "key": "test_key",
                    "title": "Test",
                    "value_type": "boolean",
                    "value": "false",
                }
            ],
            [
                {
                    "id": 1,
                    "key": "test_key",
                    "title": "Test",
                    "value_type": "boolean",
                    "value": "true",
                }
            ],
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.update_value(1, "true")

        assert isinstance(result, SettingRecord)
        assert result.value == "true"

    def test_update_value_raises_error_when_record_not_found(self, monkeypatch, db_config):
        """Test that update_value raises ValueError when record not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            settings_db.update_value(999, "value")

    def test_delete_removes_record(self, monkeypatch, db_config):
        """Test that delete removes a setting record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "key": "test_key",
                "title": "Test",
                "value_type": "boolean",
                "value": "false",
            }
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        result = settings_db.delete(1)

        assert isinstance(result, SettingRecord)
        assert result.id == 1

    def test_delete_raises_error_when_record_not_found(self, monkeypatch, db_config):
        """Test that delete raises ValueError when record not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.admin.domain.db.db_settings.Database", lambda db_data: mock_db)

        settings_db = SettingsDB(db_config)
        with pytest.raises(ValueError, match="not found"):
            settings_db.delete(999)
