"""
Unit tests for domain.models.mdwiki_revid module.

Tests for MdwikiRevidRecord.
"""

from src.sqlalchemy_app.db_models.public_models import (
    MdwikiRevidRecord,
)


class TestMdwikiRevidRecord:
    """Tests for MdwikiRevidRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating MdwikiRevidRecord with required fields."""
        record = MdwikiRevidRecord(
            title="TestArticle",
            revid=12345,
        )
        assert record.title == "TestArticle"
        assert record.revid == 12345

    def test_to_dict(self):
        """Test converting MdwikiRevidRecord to dictionary."""
        record = MdwikiRevidRecord(
            title="TestArticle",
            revid=12345,
        )
        result = record.to_dict()
        assert result == {
            "title": "TestArticle",
            "revid": 12345,
        }
