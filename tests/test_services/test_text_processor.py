"""Tests for services.text_processor module."""

import pytest

from src.app_main.services.text_processor import do_changes_to_text, DoChangesToText1

@pytest.mark.skip
class TestDoChangesToText:
    """Tests for do_changes_to_text function."""

    @pytest.mark.skipif(DoChangesToText1 is None, reason="DoChangesToText1 not available")
    def test_returns_text_some_changes(self):
        """Test that text is returned with changes (placeholder behavior)."""
        text = "Some wiki text content"
        result = do_changes_to_text(
            sourcetitle="Source",
            title="Target",
            text=text,
            lang="ar",
            mdwiki_revid="12345",
        )
        expected = "Some wiki text content\n[[Category:Translated from MDWiki]]\n"
        assert result == expected

    @pytest.mark.skipif(DoChangesToText1 is not None, reason="DoChangesToText1 is available")
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
