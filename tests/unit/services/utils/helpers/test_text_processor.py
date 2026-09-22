"""
Tests for clients.text_processor module.
"""

from src.main_app.services.utils.helpers.text_processor import fix_one_page, do_changes_to_text_with_settings  # noqa: F401

class TestFixOnePage:
    """Tests for fix_one_page function."""

    def test_import(self):
        """Test that fix_one_page is imported correctly."""
        assert fix_one_page is not None
        assert callable(fix_one_page)
