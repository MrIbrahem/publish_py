"""
Unit tests for domain.models.report module.

Tests for ReportRecord.
"""

from datetime import datetime

from src.sqlalchemy_app.db_models import (
    ReportRecord,
)


class TestReportRecord:
    """Tests for ReportRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating ReportRecord with required fields."""

        record = ReportRecord(
            id=1,
            date=datetime.now(),
            title="Test",
            user="User",
            lang="ar",
            sourcetitle="Source",
            result="success",
            data="{}",
        )
        assert record.id == 1
        assert record.title == "Test"

    def test_to_dict_converts_date_to_iso(self):
        """Test that to_dict converts date to ISO format."""

        record = ReportRecord(
            id=1,
            date=datetime(2024, 1, 1, 12, 0, 0),
            title="Test",
            user="User",
            lang="ar",
            sourcetitle="Source",
            result="success",
            data="{}",
        )
        result = record.to_dict()

        assert result["date"] == "2024-01-01T12:00:00"
        assert result["id"] == 1
        assert result["title"] == "Test"

    def test_to_dict_handles_none_date(self):
        """Test that to_dict handles None date."""

        record = ReportRecord(
            id=1,
            date=None,
            title="Test",
            user="User",
            lang="ar",
            sourcetitle="Source",
            result="success",
            data="{}",
        )
        result = record.to_dict()
        assert result["date"] == ""
