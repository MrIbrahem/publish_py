"""
Unit tests for domain.models.coordinator module.

Tests for CoordinatorRecord.
"""

from src.app_main.admin.domain.models.coordinator import (
    CoordinatorRecord,
)


class TestCoordinatorRecord:
    """Tests for CoordinatorRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating CoordinatorRecord with required fields."""
        record = CoordinatorRecord(id=1, user="TestUser")
        assert record.id == 1
        assert record.user == "TestUser"
        assert record.active == 1  # Default value

    def test_create_with_all_fields(self):
        """Test creating CoordinatorRecord with all fields."""
        record = CoordinatorRecord(id=1, user="TestUser", active=0)
        assert record.id == 1
        assert record.user == "TestUser"
        assert record.active == 0

    def test_to_dict(self):
        """Test converting CoordinatorRecord to dictionary."""
        record = CoordinatorRecord(id=1, user="TestUser", active=1)
        result = record.to_dict()
        assert result == {
            "id": 1,
            "user": "TestUser",
            "active": 1,
        }
