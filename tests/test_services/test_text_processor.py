"""Tests for services.text_processor module."""

import pytest

from src.app_main.services.text_processor import do_changes_to_text


class TestDoChangesToText:
    """Tests for do_changes_to_text function."""

    def test_returns_text_unchanged(self):
        """Test that text is returned unchanged (placeholder behavior)."""
        text = "Some wiki text content"
        result = do_changes_to_text(
            sourcetitle="Source",
            title="Target",
            text=text,
            lang="ar",
            mdwiki_revid="12345",
        )
        assert result == text

    def test_handles_empty_text(self):
        """Test that empty text is handled correctly."""
        result = do_changes_to_text(
            sourcetitle="Source",
            title="Target",
            text="",
            lang="ar",
            mdwiki_revid="12345",
        )
        assert result == ""
