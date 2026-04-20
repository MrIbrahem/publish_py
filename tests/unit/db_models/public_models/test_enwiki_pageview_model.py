"""
Unit tests for domain.models.enwiki_pageview module.

Tests for EnwikiPageviewRecord.
"""

from src.sqlalchemy_app.db_models.public_models import (
    EnwikiPageviewRecord,
)


class TestEnwikiPageviewRecord:
    """Tests for EnwikiPageviewRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating EnwikiPageviewRecord with required fields."""
        record = EnwikiPageviewRecord(id=1, title="TestArticle")
        assert record.id == 1
        assert record.title == "TestArticle"
        assert record.en_views == 0  # Default value

    def test_create_with_all_fields(self):
        """Test creating EnwikiPageviewRecord with all fields."""
        record = EnwikiPageviewRecord(
            id=1,
            title="TestArticle",
            en_views=10000,
        )
        assert record.id == 1
        assert record.title == "TestArticle"
        assert record.en_views == 10000

    def test_to_dict(self):
        """Test converting EnwikiPageviewRecord to dictionary."""
        record = EnwikiPageviewRecord(
            id=1,
            title="TestArticle",
            en_views=5000,
        )
        result = record.to_dict()
        assert result == {
            "id": 1,
            "title": "TestArticle",
            "en_views": 5000,
        }
