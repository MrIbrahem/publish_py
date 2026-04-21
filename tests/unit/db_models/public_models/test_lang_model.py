"""
Unit tests for domain.models.lang module.

Tests for LangRecord.
"""

from src.sqlalchemy_app.sqlalchemy_models import LangRecord


class TestLangRecord:
    """Tests for LangRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating LangRecord with required fields."""
        record = LangRecord(
            lang_id=1,
            code="ar",
            autonym="العربية",
            name="Arabic",
        )
        assert record.lang_id == 1
        assert record.code == "ar"
        assert record.autonym == "العربية"
        assert record.name == "Arabic"

    def test_to_dict(self):
        """Test converting LangRecord to dictionary."""
        record = LangRecord(
            lang_id=1,
            code="en",
            autonym="English",
            name="English",
        )
        result = record.to_dict()
        assert result == {
            "lang_id": 1,
            "code": "en",
            "autonym": "English",
            "name": "English",
        }
