"""
Unit tests for domain.models.translate_type module.

Tests for TranslateTypeRecord.
"""

from src.sqlalchemy_app.db_models import (
    TranslateTypeRecord,
)


class TestTranslateTypeRecord:
    """Tests for TranslateTypeRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating TranslateTypeRecord with required fields."""
        record = TranslateTypeRecord(
            tt_id=1,
            tt_title="TestArticle",
        )
        assert record.tt_id == 1
        assert record.tt_title == "TestArticle"
        assert record.tt_lead == 1  # Default value
        assert record.tt_full == 0  # Default value

    def test_create_with_all_fields(self):
        """Test creating TranslateTypeRecord with all fields."""
        record = TranslateTypeRecord(
            tt_id=1,
            tt_title="TestArticle",
            tt_lead=0,
            tt_full=1,
        )
        assert record.tt_id == 1
        assert record.tt_title == "TestArticle"
        assert record.tt_lead == 0
        assert record.tt_full == 1

    def test_to_dict(self):
        """Test converting TranslateTypeRecord to dictionary."""
        record = TranslateTypeRecord(
            tt_id=1,
            tt_title="TestArticle",
            tt_lead=1,
            tt_full=0,
        )
        result = record.to_dict()
        assert result == {
            "tt_id": 1,
            "tt_title": "TestArticle",
            "tt_lead": 1,
            "tt_full": 0,
        }
