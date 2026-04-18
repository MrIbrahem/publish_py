"""
Unit tests for domain.models.pages_users_to_main module.

Tests for PagesUsersToMainRecord.
"""

from src.app_main.public.domain.models import (
    PagesUsersToMainRecord,
)


class TestPagesUsersToMainRecord:
    """Tests for PagesUsersToMainRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating PagesUsersToMainRecord with required fields."""
        record = PagesUsersToMainRecord(id=1)
        assert record.id == 1
        assert record.new_target == ""  # Default value
        assert record.new_user == ""  # Default value
        assert record.new_qid == ""  # Default value

    def test_create_with_all_fields(self):
        """Test creating PagesUsersToMainRecord with all fields."""
        record = PagesUsersToMainRecord(
            id=1,
            new_target="TargetPage",
            new_user="TestUser",
            new_qid="Q12345",
        )
        assert record.id == 1
        assert record.new_target == "TargetPage"
        assert record.new_user == "TestUser"
        assert record.new_qid == "Q12345"

    def test_to_dict(self):
        """Test converting PagesUsersToMainRecord to dictionary."""
        record = PagesUsersToMainRecord(
            id=1,
            new_target="TargetPage",
            new_user="TestUser",
            new_qid="Q12345",
        )
        result = record.to_dict()
        assert result == {
            "id": 1,
            "new_target": "TargetPage",
            "new_user": "TestUser",
            "new_qid": "Q12345",
        }
