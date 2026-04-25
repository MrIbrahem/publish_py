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
            "redirects": None,
        }


class TestLangRecordRedirects:
    """Tests for LangRecord dataclass."""

    def test_create_with_redirects(self):
        """Test creating LangRecord with redirects (JSON list)."""
        redirects_list = ["ara", "ar-SA", "ar-EG"]
        record = LangRecord(
            lang_id=1,
            code="ar",
            autonym="العربية",
            name="Arabic",
            redirects=redirects_list
        )
        assert record.redirects == redirects_list
        assert isinstance(record.redirects, list)

    def test_to_dict_with_redirects(self):
        """Test converting LangRecord to dictionary including redirects."""
        redirects_list = ["en-US", "en-GB"]
        record = LangRecord(
            lang_id=1,
            code="en",
            autonym="English",
            name="English",
            redirects=redirects_list
        )
        result = record.to_dict()
        assert result["redirects"] == redirects_list
        # التأكد من أن القيمة المسترجعة هي مصفوفة وليست نصاً عادياً
        assert len(result["redirects"]) == 2

    def test_redirects_default_is_none(self):
        """Test that redirects defaults to None when not provided."""
        record = LangRecord(
            lang_id=2,
            code="fr",
            autonym="Français",
            name="French"
        )
        assert record.redirects is None
