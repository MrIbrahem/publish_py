"""
Unit tests for domain.models.assessment module.

Tests for AssessmentRecord.
"""

from src.sqlalchemy_app.shared.db_models.public_models import (
    AssessmentRecord,
)


class TestAssessmentRecord:
    """Tests for AssessmentRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating AssessmentRecord with required fields."""
        record = AssessmentRecord(id=1, title="TestArticle")
        assert record.id == 1
        assert record.title == "TestArticle"
        assert record.importance is None

    def test_create_with_all_fields(self):
        """Test creating AssessmentRecord with all fields."""
        record = AssessmentRecord(
            id=1,
            title="TestArticle",
            importance="High",
        )
        assert record.id == 1
        assert record.title == "TestArticle"
        assert record.importance == "High"

    def test_to_dict(self):
        """Test converting AssessmentRecord to dictionary."""
        record = AssessmentRecord(
            id=1,
            title="TestArticle",
            importance="Medium",
        )
        result = record.to_dict()
        assert result == {
            "id": 1,
            "title": "TestArticle",
            "importance": "Medium",
        }

    def test_to_dict_with_none_importance(self):
        """Test converting AssessmentRecord to dictionary with None importance."""
        record = AssessmentRecord(id=1, title="TestArticle")
        result = record.to_dict()
        assert result == {
            "id": 1,
            "title": "TestArticle",
            "importance": None,
        }
