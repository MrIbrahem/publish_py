"""
Unit tests for src/sqlalchemy_app/admin/routes/settings.py module.
"""

from __future__ import annotations

import json

import pytest
from src.sqlalchemy_app.admin.routes.settings import _parse_setting_value


class TestParseSettingValue:
    """Unit tests for _parse_setting_value function."""

    def test_parse_boolean_true_when_on(self):
        """Test that boolean type returns True when value is 'on'."""
        result, success = _parse_setting_value("boolean", "on")
        assert result is True
        assert success is True

    def test_parse_boolean_false_when_empty(self):
        """Test that boolean type returns False when value is empty."""
        result, success = _parse_setting_value("boolean", "")
        assert result is False
        assert success is True

    def test_parse_boolean_false_when_any_other_value(self):
        """Test that boolean type returns False for any non-'on' value."""
        result, success = _parse_setting_value("boolean", "off")
        assert result is False
        assert success is True

        result, success = _parse_setting_value("boolean", "anything")
        assert result is False
        assert success is True

    def test_parse_integer_valid(self):
        """Test that integer type parses valid integer strings."""
        result, success = _parse_setting_value("integer", "42")
        assert result == 42
        assert success is True

    def test_parse_integer_zero(self):
        """Test that integer type parses zero correctly."""
        result, success = _parse_setting_value("integer", "0")
        assert result == 0
        assert success is True

    def test_parse_integer_negative(self):
        """Test that integer type parses negative numbers."""
        result, success = _parse_setting_value("integer", "-10")
        assert result == -10
        assert success is True

    def test_parse_integer_invalid_returns_zero(self):
        """Test that invalid integer string returns 0 and success=True."""
        # Note: The implementation returns 0 with success=True for invalid integers
        result, success = _parse_setting_value("integer", "not_a_number")
        assert result == 0
        assert success is True

    def test_parse_integer_empty_returns_zero(self):
        """Test that empty string returns 0 for integer type."""
        result, success = _parse_setting_value("integer", "")
        assert result == 0
        assert success is True

    def test_parse_json_valid_object(self):
        """Test that json type parses valid JSON object."""
        json_str = '{"key": "value", "number": 123}'
        result, success = _parse_setting_value("json", json_str)
        assert result == {"key": "value", "number": 123}
        assert success is True

    def test_parse_json_valid_array(self):
        """Test that json type parses valid JSON array."""
        json_str = '[1, 2, 3, "test"]'
        result, success = _parse_setting_value("json", json_str)
        assert result == [1, 2, 3, "test"]
        assert success is True

    def test_parse_json_valid_string(self):
        """Test that json type parses valid JSON string."""
        json_str = '"simple string"'
        result, success = _parse_setting_value("json", json_str)
        assert result == "simple string"
        assert success is True

    def test_parse_json_valid_number(self):
        """Test that json type parses valid JSON number."""
        json_str = "42.5"
        result, success = _parse_setting_value("json", json_str)
        assert result == 42.5
        assert success is True

    def test_parse_json_valid_boolean(self):
        """Test that json type parses valid JSON boolean."""
        result, success = _parse_setting_value("json", "true")
        assert result is True
        assert success is True

        result, success = _parse_setting_value("json", "false")
        assert result is False
        assert success is True

    def test_parse_json_valid_null(self):
        """Test that json type parses valid JSON null."""
        result, success = _parse_setting_value("json", "null")
        assert result is None
        assert success is True

    def test_parse_json_invalid_returns_none_and_failure(self):
        """Test that invalid JSON returns None and success=False."""
        result, success = _parse_setting_value("json", "not valid json")
        assert result is None
        assert success is False

    def test_parse_json_invalid_syntax_returns_none_and_failure(self):
        """Test that JSON with syntax errors returns None and success=False."""
        result, success = _parse_setting_value("json", '{"unclosed": "string}')
        assert result is None
        assert success is False

    def test_parse_json_empty_returns_none_and_failure(self):
        """Test that empty string returns None and success=False for json type."""
        result, success = _parse_setting_value("json", "")
        assert result is None
        assert success is False

    def test_parse_string_type_returns_raw_value(self):
        """Test that unknown type returns raw value unchanged."""
        result, success = _parse_setting_value("string", "any value here")
        assert result == "any value here"
        assert success is True

    def test_parse_string_type_with_empty_value(self):
        """Test that string type with empty value returns empty string."""
        result, success = _parse_setting_value("string", "")
        assert result == ""
        assert success is True

    def test_parse_unknown_type_returns_raw_value(self):
        """Test that any unknown type returns raw value unchanged."""
        for v_type in ["text", "float", "date", "custom_type"]:
            result, success = _parse_setting_value(v_type, "test_value")
            assert result == "test_value"
            assert success is True

    def test_parse_unicode_values(self):
        """Test that unicode values are handled correctly."""
        # String type with unicode
        result, success = _parse_setting_value("string", "héllo wörld 日本語")
        assert result == "héllo wörld 日本語"
        assert success is True

        # JSON type with unicode
        json_str = '{"message": "héllo wörld 日本語"}'
        result, success = _parse_setting_value("json", json_str)
        assert result == {"message": "héllo wörld 日本語"}
        assert success is True

    def test_parse_special_characters_in_string(self):
        """Test that special characters in strings are preserved."""
        special_values = [
            "value with spaces",
            "value\twith\ttabs",
            "value\nwith\nnewlines",
            "<script>alert('xss')</script>",
            "quotes ' and \"",
        ]

        for value in special_values:
            result, success = _parse_setting_value("string", value)
            assert result == value
            assert success is True

    def test_parse_nested_json(self):
        """Test that nested JSON objects are parsed correctly."""
        nested_json = json.dumps({"level1": {"level2": {"level3": ["item1", "item2"]}}})
        result, success = _parse_setting_value("json", nested_json)
        assert result["level1"]["level2"]["level3"] == ["item1", "item2"]
        assert success is True

    def test_parse_json_with_special_characters(self):
        """Test that JSON with special characters is parsed correctly."""
        json_str = '{"special": "quotes \' and \\" and backslash \\\\"}'
        result, success = _parse_setting_value("json", json_str)
        assert result["special"] == "quotes ' and \" and backslash \\"
        assert success is True
