"""
Unit tests for domain.models.refs_count module.

Tests for RefsCountRecord.
"""

from src.sqlalchemy_app.db_models import (
    RefsCountRecord,
)


class TestRefsCountRecord:
    """Tests for RefsCountRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating RefsCountRecord with required fields."""
        record = RefsCountRecord(
            r_id=1,
            r_title="TestArticle",
        )
        assert record.r_id == 1
        assert record.r_title == "TestArticle"
        assert record.r_lead_refs is None
        assert record.r_all_refs is None

    def test_create_with_all_fields(self):
        """Test creating RefsCountRecord with all fields."""
        record = RefsCountRecord(
            r_id=1,
            r_title="TestArticle",
            r_lead_refs=5,
            r_all_refs=20,
        )
        assert record.r_id == 1
        assert record.r_title == "TestArticle"
        assert record.r_lead_refs == 5
        assert record.r_all_refs == 20

    def test_to_dict(self):
        """Test converting RefsCountRecord to dictionary."""
        record = RefsCountRecord(
            r_id=1,
            r_title="TestArticle",
            r_lead_refs=5,
            r_all_refs=20,
        )
        result = record.to_dict()
        assert result == {
            "r_id": 1,
            "r_title": "TestArticle",
            "r_lead_refs": 5,
            "r_all_refs": 20,
        }
