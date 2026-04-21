"""
Unit tests for domain.models.user module.

Tests for UserRecord.
"""

from datetime import datetime

from src.sqlalchemy_app.db_models import UserRecord


class TestUserRecord:
    """Tests for UserRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating UserRecord with required fields."""
        record = UserRecord(
            user_id=1,
            username="TestUser",
        )
        assert record.user_id == 1
        assert record.username == "TestUser"
        assert record.email == ""  # Default value
        assert record.wiki == ""  # Default value
        assert record.user_group == "Uncategorized"  # Default value
        assert record.reg_date is None

    def test_create_with_all_fields(self):
        """Test creating UserRecord with all fields."""
        now = datetime.now()
        record = UserRecord(
            user_id=1,
            username="TestUser",
            email="test@example.com",
            wiki="enwiki",
            user_group="Translator",
            reg_date=now,
        )
        assert record.user_id == 1
        assert record.username == "TestUser"
        assert record.email == "test@example.com"
        assert record.wiki == "enwiki"
        assert record.user_group == "Translator"
        assert record.reg_date == now

    def test_to_dict(self):
        """Test converting UserRecord to dictionary."""
        record = UserRecord(
            user_id=1,
            username="TestUser",
            email="test@example.com",
            wiki="enwiki",
            user_group="Translator",
            reg_date=None,
        )
        result = record.to_dict()
        assert result == {
            "user_id": 1,
            "username": "TestUser",
            "email": "test@example.com",
            "wiki": "enwiki",
            "user_group": "Translator",
            "reg_date": None,
        }
