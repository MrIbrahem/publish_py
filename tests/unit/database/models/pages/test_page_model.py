"""
Unit tests for domain.models.page module.

Tests for PageRecord.
"""

import pytest

from src.main_app.database.models.pages import PageRecord, PageSharedRecord, UserPageRecord


@pytest.fixture
def sample_page_row():
    """Fixture for a sample page row from database."""
    return {
        "id": 1,
        "title": "TestPage",
        "word": 100,
        "translate_type": "Lead",
        "cat": "Category:Health",
        "lang": "ar",
        "user": "TestUser",
        "target": "TargetPage",
        "date": "2024-01-01",
        "pupdate": "2024-01-01",
        "add_date": "2024-01-01",
        "deleted": 0,
        "mdwiki_revid": 12345,
    }


class PagesTests:
    """Tests for PageRecord dataclass."""

    record_type: type[PageSharedRecord]

    def test_create_with_required_fields(self):
        """Test creating PageRecord with required fields."""
        record = self.record_type(id=1, title="TestPage")
        assert record.id == 1
        assert record.title == "TestPage"
        assert record.word is None
        assert record.deleted == 0  # Default value

    def test_create_with_all_fields(self, sample_page_row):
        """Test creating PageRecord with all fields."""
        record = self.record_type(**sample_page_row)
        assert record.id == 1
        assert record.title == "TestPage"
        assert record.word == 100
        assert record.translate_type == "Lead"
        assert record.mdwiki_revid == 12345


class TestPageRecord(PagesTests):
    """Tests for PageRecord dataclass."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.record_type = PageRecord


class TestUserPageRecord(PagesTests):
    """Tests for UserPageRecord dataclass."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.record_type = UserPageRecord
