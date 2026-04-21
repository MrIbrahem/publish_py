"""
Unit tests for domain.models.setting module.

Tests for SettingRecord.
"""

# from src.sqlalchemy_app.sqlalchemy_models import SettingRecord
from src.sqlalchemy_app.sqlalchemy_models import SettingRecord


class TestSettingRecord:
    """Tests for SettingRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating SettingRecord with required fields."""
        record = SettingRecord(
            id=1,
            key="test_key",
            title="Test Setting",
        )
        assert record.id == 1
        assert record.key == "test_key"
        assert record.title == "Test Setting"
        assert record.value_type == "boolean"  # Default value
        assert record.value is None

    def test_create_with_all_fields(self):
        """Test creating SettingRecord with all fields."""
        record = SettingRecord(
            id=1,
            key="test_key",
            title="Test Setting",
            value_type="string",
            value="test value",
        )
        assert record.id == 1
        assert record.key == "test_key"
        assert record.title == "Test Setting"
        assert record.value_type == "string"
        assert record.value == "test value"

    def test_to_dict(self):
        """Test converting SettingRecord to dictionary."""
        record = SettingRecord(
            id=1,
            key="test_key",
            title="Test Setting",
            value_type="boolean",
            value="true",
        )
        result = record.to_dict()
        assert result == {
            "id": 1,
            "key": "test_key",
            "title": "Test Setting",
            "value_type": "boolean",
            "value": "true",
        }
