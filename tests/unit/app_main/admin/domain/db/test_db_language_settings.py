"""
Unit tests for db.db_language_settings module.

Tests for LanguageSettings database operations.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pymysql
import pytest
from src.app_main.admin.domain.db.db_language_settings import LanguageSettingsDB
from src.db_models.admin_models import LanguageSettingRecord
from src.app_main.config import DbConfig


class TestLanguageSettingsDB:
    """Tests for LanguageSettingsDB class."""

    def test_fetch_by_id_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns record when ID exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "lang_code": "en", "move_dots": 1, "expend": 0, "add_en_lang": 1, "add_en_lng": 0}
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_language_settings.Database", lambda db_data: mock_db)

        settings_db = LanguageSettingsDB(db_config)
        result = settings_db.fetch_by_id(1)

        assert isinstance(result, LanguageSettingRecord)
        assert result.id == 1
        assert result.lang_code == "en"

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when ID not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.admin.domain.db.db_language_settings.Database", lambda db_data: mock_db)

        settings_db = LanguageSettingsDB(db_config)
        result = settings_db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_lang_code_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_lang_code returns record when lang_code exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "lang_code": "ar", "move_dots": 0, "expend": 1, "add_en_lang": 0, "add_en_lng": 1}
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_language_settings.Database", lambda db_data: mock_db)

        settings_db = LanguageSettingsDB(db_config)
        result = settings_db.fetch_by_lang_code("ar")

        assert isinstance(result, LanguageSettingRecord)
        assert result.lang_code == "ar"

    def test_list_returns_all_records(self, monkeypatch, db_config):
        """Test that list returns all language setting records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "lang_code": "en", "move_dots": 1, "expend": 0, "add_en_lang": 1, "add_en_lng": 0},
            {"id": 2, "lang_code": "ar", "move_dots": 0, "expend": 1, "add_en_lang": 0, "add_en_lng": 1},
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_language_settings.Database", lambda db_data: mock_db)

        settings_db = LanguageSettingsDB(db_config)
        result = settings_db.list()

        assert len(result) == 2
        assert all(isinstance(r, LanguageSettingRecord) for r in result)

    def test_add_inserts_new_record(self, monkeypatch, db_config):
        """Test that add inserts a new language setting record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "lang_code": "fr", "move_dots": 0, "expend": 0, "add_en_lang": 0, "add_en_lng": 0}
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_language_settings.Database", lambda db_data: mock_db)

        settings_db = LanguageSettingsDB(db_config)
        result = settings_db.add("fr", 0, 0, 0, 0)

        assert isinstance(result, LanguageSettingRecord)
        assert result.lang_code == "fr"

    def test_add_raises_error_when_lang_code_empty(self, monkeypatch, db_config):
        """Test that add raises ValueError when lang_code is empty."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.admin.domain.db.db_language_settings.Database", lambda db_data: mock_db)

        settings_db = LanguageSettingsDB(db_config)
        with pytest.raises(ValueError, match="Language code is required"):
            settings_db.add("")

    def test_update_modifies_record(self, monkeypatch, db_config):
        """Test that update modifies a language setting record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.side_effect = [
            [{"id": 1, "lang_code": "en", "move_dots": 0, "expend": 0, "add_en_lang": 0, "add_en_lng": 0}],
            [{"id": 1, "lang_code": "en", "move_dots": 1, "expend": 1, "add_en_lang": 1, "add_en_lng": 1}],
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_language_settings.Database", lambda db_data: mock_db)

        settings_db = LanguageSettingsDB(db_config)
        result = settings_db.update(1, move_dots=1, expend=1, add_en_lang=1, add_en_lng=1)

        assert isinstance(result, LanguageSettingRecord)
        assert result.move_dots == 1

    def test_delete_removes_record(self, monkeypatch, db_config):
        """Test that delete removes a language setting record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "lang_code": "en", "move_dots": 0, "expend": 0, "add_en_lang": 0, "add_en_lng": 0}
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_language_settings.Database", lambda db_data: mock_db)

        settings_db = LanguageSettingsDB(db_config)
        result = settings_db.delete(1)

        assert isinstance(result, LanguageSettingRecord)

    def test_add_or_update_upserts_record(self, monkeypatch, db_config):
        """Test that add_or_update upserts a language setting record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "lang_code": "de", "move_dots": 1, "expend": 0, "add_en_lang": 1, "add_en_lng": 0}
        ]

        monkeypatch.setattr("src.app_main.admin.domain.db.db_language_settings.Database", lambda db_data: mock_db)

        settings_db = LanguageSettingsDB(db_config)
        result = settings_db.add_or_update("de", 1, 0, 1, 0)

        assert isinstance(result, LanguageSettingRecord)
        assert result.lang_code == "de"
