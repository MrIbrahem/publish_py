from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.admin.services.setting_service import (
    add_setting,
    delete_setting,
    get_setting,
    get_setting_by_key,
    list_settings,
    update_value,
)

# from src.sqlalchemy_app.sqlalchemy_models import SettingRecord
from src.sqlalchemy_app.sqlalchemy_models import SettingRecord


def test_setting_workflow():
    # Test add
    s = add_setting("site_name", "Application Name", "string", "WikiMedical")
    assert s.key == "site_name"
    assert s.value == "WikiMedical"

    # Test get
    s2 = get_setting(s.id)
    assert s2.key == "site_name"

    # Test get by key
    s3 = get_setting_by_key("site_name")
    assert s3.id == s.id

    # Test list
    all_s = list_settings()
    assert any(x.key == "site_name" for x in all_s)

    # Test update
    updated = update_value(s.id, "MDWiki")
    assert updated.value == "MDWiki"

    # Test delete
    delete_setting(s.id)
    assert get_setting(s.id) is None


class TestListSettings:
    """Tests for list_settings function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_settings returns all records."""
        add_setting("maintenance_mode", "Maintenance Status", "boolean", "False")
        add_setting("max_upload_size", "Maximum File Size", "integer", "10485760")
        result = list_settings()
        assert len(result) >= 2


class TestGetSetting:
    """Tests for get_setting function."""

    def test_returns_setting_record(self, monkeypatch):
        """Test that function returns a SettingRecord."""
        s = add_setting("analytics_id", "Google Analytics ID", "string", "UA-12345")
        result = get_setting(s.id)
        assert isinstance(result, SettingRecord)
        assert result.key == "analytics_id"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_setting(9999) is None


class TestGetSettingByKey:
    """Tests for get_setting_by_key function."""

    def test_returns_setting_by_key(self, monkeypatch):
        """Test that function returns a SettingRecord by key."""
        add_setting("api_timeout", "API Timeout Seconds", "integer", "30")
        result = get_setting_by_key("api_timeout")
        assert result.key == "api_timeout"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_setting_by_key("ghost") is None


class TestAddSetting:
    """Tests for add_setting function."""

    def test_adds_setting_and_returns_record(self, monkeypatch):
        """Test that add_setting adds and returns the record."""
        record = add_setting("debug_logging", "Enable Debug Logs", "boolean", "True")
        assert record.key == "debug_logging"

    def test_raises_error_if_exists(self, monkeypatch):
        add_setting("K1", "T1")
        with pytest.raises(ValueError, match="already exists"):
            add_setting("K1", "T1")

    def test_raises_error_if_no_key_or_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Key is required"):
            add_setting("", "Title")
        with pytest.raises(ValueError, match="Title is required"):
            add_setting("Key", "")


class TestUpdateValue:
    """Tests for update_value function."""

    def test_updates_setting_value(self, monkeypatch):
        """Test that update_value updates the setting value."""
        s = add_setting("items_per_page", "Search results limit", value_type="integer", value="20")
        updated = update_value(s.id, "50")
        assert updated.value == "50"

    def test_handles_none_value(self, monkeypatch):
        s = add_setting("nullable_setting", "Title", value="Something")
        updated = update_value(s.id, None)
        assert updated.value is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_value(9999, "NewValue")


class TestDeleteSetting:
    """Tests for delete_setting function."""

    def test_deletes_setting(self, monkeypatch):
        """Test that delete_setting calls store delete."""
        s = add_setting("temporary_key", "Will be deleted")
        delete_setting(s.id)
        assert get_setting(s.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_setting(9999)
