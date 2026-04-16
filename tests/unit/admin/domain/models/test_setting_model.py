"""
Unit tests for domain.models.setting module.

Tests for SettingRecord.
"""

from src.app_main.admin.domain.models.setting import (
    SettingRecord,
)


class TestSettingRecord:
    """Tests for SettingRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating SettingRecord with required fields."""
        record = SettingRecord(
            id=1,
            title="test_setting",
            displayed="Test Setting",
        )
        assert record.id == 1
        assert record.title == "test_setting"
        assert record.displayed == "Test Setting"
        assert record.Type == "check"  # Default value
        assert record.value == 0
        assert record.ignored == 0

    def test_create_with_all_fields(self):
        """Test creating SettingRecord with all fields."""
        record = SettingRecord(
            id=1,
            title="test_setting",
            displayed="Test Setting",
            Type="text",
            value=1,
            ignored=1,
        )
        assert record.id == 1
        assert record.title == "test_setting"
        assert record.displayed == "Test Setting"
        assert record.Type == "text"
        assert record.value == 1
        assert record.ignored == 1

    def test_to_dict(self):
        """Test converting SettingRecord to dictionary."""
        record = SettingRecord(
            id=1,
            title="test_setting",
            displayed="Test Setting",
            Type="check",
            value=1,
            ignored=0,
        )
        result = record.to_dict()
        assert result == {
            "id": 1,
            "title": "test_setting",
            "displayed": "Test Setting",
            "Type": "check",
            "value": 1,
            "ignored": 0,
        }
