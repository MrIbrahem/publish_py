"""
Tests for shared.utils.web_utils module.
"""

from __future__ import annotations

import pytest
from src.sqlalchemy_app.shared.utils.web_utils import parse_select_fields


class TestParseSelectFields:
    """Tests for parse_select_fields function."""

    def test_returns_none_for_none_input(self):
        """Test that None input returns None."""
        result = parse_select_fields(None)
        assert result is None

    def test_returns_none_for_empty_string(self):
        """Test that empty string returns None."""
        result = parse_select_fields("")
        assert result is None

    def test_parses_single_field(self):
        """Test parsing a single field name."""
        result = parse_select_fields("field1")
        assert result == ["field1"]

    def test_parses_multiple_fields(self):
        """Test parsing multiple comma-separated fields."""
        result = parse_select_fields("field1,field2,field3")
        assert result == ["field1", "field2", "field3"]

    def test_strips_whitespace_from_fields(self):
        """Test that whitespace is stripped from field names."""
        result = parse_select_fields("  field1  ,  field2  ,  field3  ")
        assert result == ["field1", "field2", "field3"]

    def test_handles_mixed_whitespace(self):
        """Test handling various whitespace patterns."""
        result = parse_select_fields("field1 ,field2, field3,  field4   ,   field5")
        assert result == ["field1", "field2", "field3", "field4", "field5"]

    def test_handles_empty_field_between_commas(self):
        """Test that empty fields between commas are filtered out."""
        result = parse_select_fields("field1,,field2")
        assert result == ["field1", "field2"]

    def test_handles_leading_trailing_commas(self):
        """Test handling of leading and trailing commas."""
        result = parse_select_fields(",field1,field2,")
        assert result == ["field1", "field2"]

    def test_handles_only_commas(self):
        """Test that string with only commas returns empty list."""
        result = parse_select_fields(",,,")
        assert result == []

    def test_handles_whitespace_only_fields(self):
        """Test that whitespace-only fields are filtered out."""
        result = parse_select_fields("field1,   ,field2,  ,  ,field3")
        assert result == ["field1", "field2", "field3"]

    def test_preserves_field_order(self):
        """Test that field order is preserved."""
        result = parse_select_fields("z,y,x,a,b,c")
        assert result == ["z", "y", "x", "a", "b", "c"]

    def test_handles_duplicate_fields(self):
        """Test that duplicate fields are preserved."""
        result = parse_select_fields("field1,field1,field2,field1")
        assert result == ["field1", "field1", "field2", "field1"]

    def test_handles_special_characters_in_field_names(self):
        """Test handling of special characters in field names."""
        result = parse_select_fields("field_name,field-name,field.name,field123")
        assert result == ["field_name", "field-name", "field.name", "field123"]

    def test_handles_unicode_field_names(self):
        """Test handling of unicode characters in field names."""
        result = parse_select_fields("naïve,résumé,日本語,field")
        assert result == ["naïve", "résumé", "日本語", "field"]

    def test_handles_long_field_list(self):
        """Test handling of a long list of fields."""
        fields = ",".join([f"field{i}" for i in range(100)])
        result = parse_select_fields(fields)
        assert len(result) == 100
        assert result[0] == "field0"
        assert result[99] == "field99"

    def test_handles_single_field_with_whitespace(self):
        """Test parsing a single field with surrounding whitespace."""
        result = parse_select_fields("   field1   ")
        assert result == ["field1"]

    def test_handles_complex_field_names(self):
        """Test handling of complex field names like table.column."""
        result = parse_select_fields("users.name,users.email,posts.title")
        assert result == ["users.name", "users.email", "posts.title"]

    def test_returns_list_type(self):
        """Test that return type is a list."""
        result = parse_select_fields("a,b,c")
        assert isinstance(result, list)

    def test_empty_result_is_list(self):
        """Test that empty result is an empty list, not None."""
        result = parse_select_fields(",,,")
        assert result == []
        assert isinstance(result, list)
