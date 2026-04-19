from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.admin.domain_models import SettingRecord
from src.sqlalchemy_app.admin.domain.models import _SettingRecord
from src.sqlalchemy_app.admin.domain.services.setting_service import (
    add_setting,
    delete_setting,
    get_setting,
    get_setting_by_key,
    list_settings,
    update_value,
)
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.sqlalchemy_app.shared.domain.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


def test_setting_workflow():
    # Test add
    s = add_setting("test_key", "Test Title", "string", "test_value")
    assert s.key == "test_key"
    assert s.value == "test_value"

    # Test get
    s2 = get_setting(s.id)
    assert s2.key == "test_key"

    # Test get by key
    s3 = get_setting_by_key("test_key")
    assert s3.id == s.id

    # Test list
    all_s = list_settings()
    assert any(x.key == "test_key" for x in all_s)

    # Test update
    updated = update_value(s.id, "new_value")
    assert updated.value == "new_value"

    # Test delete
    delete_setting(s.id)
    assert get_setting(s.id) is None


class TestListSettings:
    """Tests for list_settings function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_settings returns all records."""
        add_setting("k1", "t1")
        add_setting("k2", "t2")
        result = list_settings()
        assert len(result) >= 2


class TestGetSetting:
    """Tests for get_setting function."""

    def test_returns_setting_record(self, monkeypatch):
        """Test that function returns a SettingRecord."""
        s = add_setting("k1", "t1")
        result = get_setting(s.id)
        assert isinstance(result, SettingRecord)
        assert result.key == "k1"


class TestGetSettingByKey:
    """Tests for get_setting_by_key function."""

    def test_returns_setting_by_key(self, monkeypatch):
        """Test that function returns a SettingRecord by key."""
        add_setting("k1", "t1")
        result = get_setting_by_key("k1")
        assert result.key == "k1"


class TestAddSetting:
    """Tests for add_setting function."""

    def test_adds_setting_and_returns_record(self, monkeypatch):
        """Test that add_setting adds and returns the record."""
        record = add_setting("k1", "t1")
        assert record.key == "k1"


class TestUpdateValue:
    """Tests for update_value function."""

    def test_updates_setting_value(self, monkeypatch):
        """Test that update_value updates the setting value."""
        s = add_setting("k1", "t1", value_type="string", value="v1")
        updated = update_value(s.id, "v2")
        assert updated.value == "v2"


class TestDeleteSetting:
    """Tests for delete_setting function."""

    def test_deletes_setting(self, monkeypatch):
        """Test that delete_setting calls store delete."""
        s = add_setting("k1", "t1")
        delete_setting(s.id)
        assert get_setting(s.id) is None
