"""
Tests for app_routes.publish.worker module.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.routes.publish.worker import (
    _get_errors_file,
    _get_revid,
    _handle_no_access,
    _process_edit,
)


class TestGetErrorsFile:
    """Tests for _get_errors_file function."""

    def test_returns_placeholder_for_unknown_error(self):
        """Test that placeholder is returned for unknown errors."""

        result = _get_errors_file({"some": "error"}, "errors")

        assert result == "errors"

    def test_returns_protectedpage_for_protected_error(self):
        """Test that protectedpage is returned for protected page error."""

        result = _get_errors_file({"error": {"code": "protectedpage"}}, "errors")

        assert result == "protectedpage"

    def test_returns_ratelimited_for_rate_limit_error(self):
        """Test that ratelimited is returned for rate limit error."""

        result = _get_errors_file({"error": {"info": "ratelimited"}}, "errors")

        assert result == "ratelimited"
