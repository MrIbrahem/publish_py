import pytest

# from src.main_app.db.models import SettingRecord
from src.main_app.db.models import SettingRecord
from src.main_app.db.services.config.settings_service import (
    create_setting,
    get_setting_by_id,
    get_setting_by_key,
    list_settings,
)
from src.main_app.db.services.delete_service import (
    delete_setting,
    delete_setting_by_key,
)


def test_setting_workflow():
    # Test add
    s = create_setting("site_name", "Application Name", "string", "WikiMedical")

    assert s is True

    # Test get by key
    s3 = get_setting_by_key("site_name")
    assert s3.key == "site_name"
    assert s3.value == "WikiMedical"

    # Test list
    all_s = list_settings()
    assert any(x.key == "site_name" for x in all_s)

    # Test delete
    deleted = delete_setting(s3.id)
    assert deleted is True
    assert get_setting_by_id(s3.id) is None


class TestListSettings:
    """Tests for list_settings function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_settings returns all records."""
        create_setting("maintenance_mode", "Maintenance Status", "boolean", "False")
        create_setting("max_upload_size", "Maximum File Size", "integer", "10485760")
        result = list_settings()
        assert len(result) >= 2


class TestGetSetting:
    """Tests for get_setting_by_id function."""

    def test_returns_setting_record(self, monkeypatch):
        """Test that function returns a SettingRecord."""
        create_setting("analytics_id", "Google Analytics ID", "string", "UA-12345")
        result = get_setting_by_key("analytics_id")
        assert isinstance(result, SettingRecord)
        assert result.key == "analytics_id"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_setting_by_id(9999) is None


class TestGetSettingByKey:
    """Tests for get_setting_by_key function."""

    def test_returns_setting_by_key(self, monkeypatch):
        """Test that function returns a SettingRecord by key."""
        create_setting("api_timeout", "API Timeout Seconds", "integer", "30")
        result = get_setting_by_key("api_timeout")
        assert result.key == "api_timeout"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_setting_by_key("ghost") is None


class TestAddSetting:
    """Tests for create_setting function."""

    def test_adds_setting_and_returns_record(self, monkeypatch):
        """Test that create_setting adds and returns the record."""
        record = create_setting("debug_logging", "Enable Debug Logs", "boolean", "True")
        assert record is True

    def test_raises_error_if_exists(self, monkeypatch):
        created = create_setting("K1", "T1")
        assert created is True

        created2 = create_setting("K1", "T1")
        assert created2 is False

    def test_raises_error_if_no_key_or_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Key is required"):
            create_setting("", "Title")
        with pytest.raises(ValueError, match="Title is required"):
            create_setting("Key", "")


class TestDeleteSetting:
    """Tests for delete_setting function."""

    def test_deletes_setting(self, monkeypatch):
        """Test that delete_setting calls store delete."""
        create_setting("temporary_key", "Will be deleted")
        deleted = delete_setting_by_key("temporary_key")
        assert deleted is True
        assert get_setting_by_key("temporary_key") is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert delete_setting(9999) is False
