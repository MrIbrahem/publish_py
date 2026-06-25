"""
Unit tests for src/main_app/admin/routes/settings.py module.
"""

from __future__ import annotations

from src.main_app.admin.routes.settings import _parse_setting_value


class TestParseSettingValue:
    """Unit tests for _parse_setting_value function."""

    def test_parse_boolean_true_when_on(self):
        """Test that boolean type returns True when value is 'on'."""
        result, success = _parse_setting_value("boolean", "on")
        assert result == 1
        assert success == 1

    def test_parse_boolean_false_when_empty(self):
        """Test that boolean type returns False when value is empty."""
        result, success = _parse_setting_value("boolean", "")
        assert result == 0
        assert success == 1

    def test_parse_boolean_false_when_any_other_value(self):
        """Test that boolean type returns False for any non-'on' value."""
        result, success = _parse_setting_value("boolean", "off")
        assert result == 0
        assert success == 1

        result, success = _parse_setting_value("boolean", "anything")
        assert result == 0
        assert success == 1

    def test_parse_integer_valid(self):
        """Test that integer type parses valid integer strings."""
        result, success = _parse_setting_value("integer", "42")
        assert result == 42
        assert success == 1

    def test_parse_integer_zero(self):
        """Test that integer type parses zero correctly."""
        result, success = _parse_setting_value("integer", "0")
        assert result == 0
        assert success == 1

    def test_parse_integer_negative(self):
        """Test that integer type parses negative numbers."""
        result, success = _parse_setting_value("integer", "-10")
        assert result == -10
        assert success == 1

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

    def test_parse_string_type_returns_raw_value(self):
        """Test that unknown type returns raw value unchanged."""
        result, success = _parse_setting_value("string", "any value here")
        assert result == "any value here"
        assert success == 1

    def test_parse_string_type_with_empty_value(self):
        """Test that string type with empty value returns empty string."""
        result, success = _parse_setting_value("string", "")
        assert result == ""
        assert success == 1

    def test_parse_unknown_type_returns_raw_value(self):
        """Test that any unknown type returns raw value unchanged."""
        for v_type in ["text", "float", "date", "custom_type"]:
            result, success = _parse_setting_value(v_type, "test_value")
            assert result == "test_value"
            assert success == 1

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
            assert success == 1
