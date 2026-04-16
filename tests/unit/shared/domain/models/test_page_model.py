"""
Unit tests for domain.models.page module.

Tests for PageRecord.
"""

from src.app_main.shared.domain.models.page import (
    PageRecord,
)


class TestPageRecord:
    """Tests for PageRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating PageRecord with required fields."""
        record = PageRecord(id=1, title="TestPage")
        assert record.id == 1
        assert record.title == "TestPage"
        assert record.word is None
        assert record.deleted == 0  # Default value

    def test_create_with_all_fields(self, sample_page_row):
        """Test creating PageRecord with all fields."""
        record = PageRecord(**sample_page_row)
        assert record.id == 1
        assert record.title == "TestPage"
        assert record.word == 100
        assert record.translate_type == "Lead"
        assert record.mdwiki_revid == 12345
