"""
Unit tests for domain.models.project module.

Tests for ProjectRecord.
"""

from src.sqlalchemy_app.db_models import (
    ProjectRecord,
)


class TestProjectRecord:
    """Tests for ProjectRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating ProjectRecord with required fields."""
        record = ProjectRecord(
            g_id=1,
            g_title="TestProject",
        )
        assert record.g_id == 1
        assert record.g_title == "TestProject"

    def test_to_dict(self):
        """Test converting ProjectRecord to dictionary."""
        record = ProjectRecord(
            g_id=1,
            g_title="TestProject",
        )
        result = record.to_dict()
        assert result == {
            "g_id": 1,
            "g_title": "TestProject",
        }
