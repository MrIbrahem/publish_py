"""
Unit tests for domain.models.in_process module.

Tests for InProcessRecord.
"""

from datetime import datetime

from src.sqlalchemy_app.shared.db_models.public_models import (
    InProcessRecord,
)


class TestInProcessRecord:
    """Tests for InProcessRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating InProcessRecord with required fields."""
        record = InProcessRecord(
            id=1,
            title="TestArticle",
            user="TestUser",
            lang="ar",
        )
        assert record.id == 1
        assert record.title == "TestArticle"
        assert record.user == "TestUser"
        assert record.lang == "ar"
        assert record.cat == "RTT"  # Default value
        assert record.translate_type == "lead"  # Default value
        assert record.word == 0  # Default value
        assert record.add_date is None

    def test_create_with_all_fields(self):
        """Test creating InProcessRecord with all fields."""
        now = datetime.now()
        record = InProcessRecord(
            id=1,
            title="TestArticle",
            user="TestUser",
            lang="ar",
            cat="Health",
            translate_type="full",
            word=500,
            add_date=now,
        )
        assert record.id == 1
        assert record.title == "TestArticle"
        assert record.user == "TestUser"
        assert record.lang == "ar"
        assert record.cat == "Health"
        assert record.translate_type == "full"
        assert record.word == 500
        assert record.add_date == now

    def test_to_dict(self):
        """Test converting InProcessRecord to dictionary."""
        record = InProcessRecord(
            id=1,
            title="TestArticle",
            user="TestUser",
            lang="en",
            cat="RTT",
            translate_type="lead",
            word=1000,
            add_date=None,
        )
        result = record.to_dict()
        assert result == {
            "id": 1,
            "title": "TestArticle",
            "user": "TestUser",
            "lang": "en",
            "cat": "RTT",
            "translate_type": "lead",
            "word": 1000,
            "add_date": None,
        }
