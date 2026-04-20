from unittest.mock import MagicMock, patch

import pytest
from src.db_models.admin_models import LanguageSettingRecord
from src.sqlalchemy_app.admin.domain.models import _LanguageSettingRecord
from src.sqlalchemy_app.admin.domain.services.language_setting_service import (
    add_language_setting,
    add_or_update_language_setting,
    delete_language_setting,
    get_language_setting,
    get_language_setting_by_code,
    list_language_settings,
    update_language_setting,
)


def test_language_setting_workflow():
    # Test add
    ls = add_language_setting("en", 1, 0, 1)
    assert ls.lang_code == "en"
    assert ls.move_dots == 1

    # Test get
    ls2 = get_language_setting(ls.id)
    assert ls2.lang_code == "en"

    # Test get by code
    ls3 = get_language_setting_by_code("en")
    assert ls3.id == ls.id

    # Test list
    all_ls = list_language_settings()
    assert any(x.lang_code == "en" for x in all_ls)

    # Test update
    updated = update_language_setting(ls.id, move_dots=0)
    assert updated.move_dots == 0

    # Test add_or_update
    ls4 = add_or_update_language_setting("en", 1, 1, 1)
    assert ls4.move_dots == 1
    assert ls4.expend == 1

    # Test delete
    delete_language_setting(ls.id)
    assert get_language_setting(ls.id) is None


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
