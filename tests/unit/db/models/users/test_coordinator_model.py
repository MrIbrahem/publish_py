"""
Unit tests for domain.models.coordinator module.

Tests for AdminUserRecord.
"""

from src.main_app.db.models import AdminUserRecord


class TestCoordinatorRecord:
    """Tests for AdminUserRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating AdminUserRecord with required fields."""
        record = AdminUserRecord(id=1, username="TestUser")
        assert record.id == 1
        assert record.username == "TestUser"
        # assert record.is_active == 1  # Default value

    def test_create_with_all_fields(self):
        """Test creating AdminUserRecord with all fields."""
        record = AdminUserRecord(id=1, username="TestUser", is_active=0)
        assert record.id == 1
        assert record.username == "TestUser"
        assert record.is_active == 0

    def test_to_dict(self):
        """Test converting AdminUserRecord to dictionary."""
        record = AdminUserRecord(id=1, username="TestUser", is_active=1)
        result = record.to_dict()
        assert result == {
            "id": 1,
            "username": "TestUser",
            "is_active": 1,
        }
