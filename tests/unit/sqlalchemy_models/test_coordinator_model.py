"""
Unit tests for domain.models.coordinator module.

Tests for CoordinatorRecord.
"""

from src.sqlalchemy_app.sqlalchemy_models import CoordinatorRecord


class TestCoordinatorRecord:
    """Tests for CoordinatorRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating CoordinatorRecord with required fields."""
        record = CoordinatorRecord(id=1, username="TestUser")
        assert record.id == 1
        assert record.username == "TestUser"
        assert record.is_active == 1  # Default value

    def test_create_with_all_fields(self):
        """Test creating CoordinatorRecord with all fields."""
        record = CoordinatorRecord(id=1, username="TestUser", is_active=0)
        assert record.id == 1
        assert record.username == "TestUser"
        assert record.is_active == 0

    def test_to_dict(self):
        """Test converting CoordinatorRecord to dictionary."""
        record = CoordinatorRecord(id=1, username="TestUser", is_active=1)
        result = record.to_dict()
        assert result == {
            "id": 1,
            "username": "TestUser",
            "is_active": 1,
        }
