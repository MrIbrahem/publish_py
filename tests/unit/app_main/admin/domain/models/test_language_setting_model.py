"""
Unit tests for domain.models.language_setting module.

Tests for LanguageSettingRecord.
"""

from src.app_main.admin.domain.admin_models import (
    LanguageSettingRecord,
)


class TestLanguageSettingRecord:
    """Tests for LanguageSettingRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating LanguageSettingRecord with required fields."""
        record = LanguageSettingRecord(id=1)
        assert record.id == 1
        assert record.lang_code is None
        assert record.move_dots == 0  # Default value
        assert record.expend == 0
        assert record.add_en_lang == 0
        assert record.add_en_lng == 0

    def test_create_with_all_fields(self):
        """Test creating LanguageSettingRecord with all fields."""
        record = LanguageSettingRecord(
            id=1,
            lang_code="ar",
            move_dots=1,
            expend=1,
            add_en_lang=1,
            add_en_lng=1,
        )
        assert record.id == 1
        assert record.lang_code == "ar"
        assert record.move_dots == 1
        assert record.expend == 1
        assert record.add_en_lang == 1
        assert record.add_en_lng == 1

    def test_to_dict(self):
        """Test converting LanguageSettingRecord to dictionary."""
        record = LanguageSettingRecord(
            id=1,
            lang_code="en",
            move_dots=1,
            expend=0,
            add_en_lang=1,
            add_en_lng=0,
        )
        result = record.to_dict()
        assert result == {
            "id": 1,
            "lang_code": "en",
            "move_dots": 1,
            "expend": 0,
            "add_en_lang": 1,
            "add_en_lng": 0,
        }
