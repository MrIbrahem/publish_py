"""
Unit tests for domain.models.word module.

Tests for WordRecord.
"""

from src.db_models.public_models import (
    WordRecord,
)


class TestWordRecord:
    """Tests for WordRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating WordRecord with required fields."""
        record = WordRecord(
            w_id=1,
            w_title="TestArticle",
        )
        assert record.w_id == 1
        assert record.w_title == "TestArticle"
        assert record.w_lead_words is None
        assert record.w_all_words is None

    def test_create_with_all_fields(self):
        """Test creating WordRecord with all fields."""
        record = WordRecord(
            w_id=1,
            w_title="TestArticle",
            w_lead_words=500,
            w_all_words=2000,
        )
        assert record.w_id == 1
        assert record.w_title == "TestArticle"
        assert record.w_lead_words == 500
        assert record.w_all_words == 2000

    def test_to_dict(self):
        """Test converting WordRecord to dictionary."""
        record = WordRecord(
            w_id=1,
            w_title="TestArticle",
            w_lead_words=500,
            w_all_words=2000,
        )
        result = record.to_dict()
        assert result == {
            "w_id": 1,
            "w_title": "TestArticle",
            "w_lead_words": 500,
            "w_all_words": 2000,
        }
