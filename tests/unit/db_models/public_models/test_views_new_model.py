"""
Unit tests for domain.models.views_new module.

Tests for ViewsNewRecord.
"""

from src.sqlalchemy_app.db_models.public_models import (
    ViewsNewRecord,
)


class TestViewsNewRecord:
    """Tests for ViewsNewRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating ViewsNewRecord with required fields."""
        record = ViewsNewRecord(
            id=1,
            target="TestArticle",
            lang="ar",
            year=2024,
        )
        assert record.id == 1
        assert record.target == "TestArticle"
        assert record.lang == "ar"
        assert record.year == 2024
        assert record.views == 0  # Default value

    def test_create_with_all_fields(self):
        """Test creating ViewsNewRecord with all fields."""
        record = ViewsNewRecord(
            id=1,
            target="TestArticle",
            lang="ar",
            year=2024,
            views=10000,
        )
        assert record.id == 1
        assert record.target == "TestArticle"
        assert record.lang == "ar"
        assert record.year == 2024
        assert record.views == 10000

    def test_to_dict(self):
        """Test converting ViewsNewRecord to dictionary."""
        record = ViewsNewRecord(
            id=1,
            target="TestArticle",
            lang="en",
            year=2024,
            views=5000,
        )
        result = record.to_dict()
        assert result == {
            "id": 1,
            "target": "TestArticle",
            "lang": "en",
            "year": 2024,
            "views": 5000,
        }
