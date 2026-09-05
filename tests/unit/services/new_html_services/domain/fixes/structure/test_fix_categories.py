"""
Unit tests for src/main_app/services/new_html_services/domain/fixes/structure/fix_categories.py module.

Functions to test: remove_categories

Ported from the PHP suite ``FixCatsTest`` (FixRefs\\Tests\\WikiTextFixes).
"""

from __future__ import annotations

from src.main_app.services.new_html_services.domain.fixes.structure.fix_categories import (
    remove_categories,
)


class TestRemoveCategories:
    """Tests for the `remove_categories` function of the `fix_categories` module."""

    def test_remove_categories_with_single_category(self):
        """A single [[Category:...]] link is removed while surrounding text remains."""
        text = "Article content [[Category:Medicine]] more text"
        result = remove_categories(text)

        assert "[[Category:Medicine]]" not in result
        assert "Article content" in result
        assert "more text" in result

    def test_remove_categories_with_multiple_categories(self):
        """Every category link in the text is removed."""
        text = "[[Category:Health]] Content [[Category:Science]] [[Category:Medicine]]"
        result = remove_categories(text)

        assert "[[Category:Health]]" not in result
        assert "[[Category:Science]]" not in result
        assert "[[Category:Medicine]]" not in result
        assert "Content" in result

    def test_remove_categories_with_sort_keys(self):
        """A category link with a sort key (piped display text) is removed as a whole."""
        text = "Text [[Category:People|Smith, John]] more"
        result = remove_categories(text)

        assert "[[Category:People|Smith, John]]" not in result
        assert "Text" in result
        assert "more" in result

    def test_remove_categories_with_no_categories(self):
        """Text without any category links is returned unchanged (after stripping)."""
        text = "Plain article text without categories"
        result = remove_categories(text)

        assert result == text

    def test_remove_categories_with_empty_text(self):
        """Empty input returns empty output."""
        result = remove_categories("")

        assert result == ""

    def test_remove_categories_preserves_other_links(self):
        """Non-category wikilinks are preserved while the category link is removed."""
        text = "[[Article link]] and [[Category:Medicine]] and [[Another link]]"
        result = remove_categories(text)

        assert "[[Article link]]" in result
        assert "[[Another link]]" in result
        assert "[[Category:Medicine]]" not in result

    def test_remove_categories_with_case_variations(self):
        """The `Category:` prefix is matched case-insensitively."""
        text = "[[Category:Test]] [[category:Test2]] [[CATEGORY:Test3]]"
        result = remove_categories(text)

        assert "Category:Test" not in result
        assert "category:Test2" not in result
        assert "CATEGORY:Test3" not in result

    def test_remove_categories_with_whitespace(self):
        """A category link with extra internal whitespace around the prefix is still removed."""
        text = "[[  Category  :  Medicine  ]] content"
        result = remove_categories(text)

        assert "Category" not in result
        assert "content" in result

    def test_remove_categories_at_end_of_article(self):
        """Trailing category links at the end of an article are all removed."""
        text = "Article content.\n\n[[Category:Medicine]]\n[[Category:Health]]\n[[Category:Science]]"
        result = remove_categories(text)

        assert "Article content." in result
        assert "[[Category:" not in result

    def test_remove_categories_with_multiple_sort_keys(self):
        """Multiple category links, each with their own sort key, are all removed."""
        text = "[[Category:People|Smith]] [[Category:Authors|Smith, John]]"
        result = remove_categories(text)

        assert "[[Category:People|Smith]]" not in result
        assert "[[Category:Authors|Smith, John]]" not in result

    def test_remove_categories_with_special_characters(self):
        """A category name with hyphens, underscores, and dots is removed."""
        text = "Content [[Category:Articles with special-characters_and.spaces]]"
        result = remove_categories(text)

        assert "[[Category:" not in result
        assert "Content" in result

    def test_remove_categories_with_newlines(self):
        """Category links surrounded by newlines are removed, preserving the newlines."""
        text = "Content\n[[Category:First]]\n[[Category:Second]]\nMore content"
        result = remove_categories(text)

        assert "Content\n" in result
        assert "More content" in result
        assert "[[Category:" not in result

    def test_remove_categories_with_duplicates(self):
        """Repeated links to the same category are all removed."""
        text = "[[Category:Test]] content [[Category:Test]]"
        result = remove_categories(text)

        assert "[[Category:Test]]" not in result
        assert "content" in result

    def test_remove_categories_with_complex_sort_key(self):
        """A category link with a sort key containing symbols and spaces is removed."""
        text = "[[Category:Articles|*Special sort key with spaces and symbols!@#]]"
        result = remove_categories(text)

        assert "[[Category:" not in result

    def test_remove_categories_preserves_templates(self):
        """Templates before and after a category link are left untouched."""
        text = "{{Template|param=value}} [[Category:Test]] {{Another template}}"
        result = remove_categories(text)

        assert "{{Template|param=value}}" in result
        assert "{{Another template}}" in result
        assert "[[Category:Test]]" not in result

    def test_remove_categories_with_multiple_spaces(self):
        """Category links separated by extra spaces are all removed."""
        text = "Text [[Category:Test1]]  [[Category:Test2]]   [[Category:Test3]]"
        result = remove_categories(text)

        assert "[[Category:" not in result
        assert "Text" in result

    def test_remove_categories_with_inline_categories(self):
        """Category links interspersed with plain text throughout are all removed."""
        text = "Start [[Category:Inline]] middle [[Category:Another]] end"
        result = remove_categories(text)

        assert "Start" in result
        assert "middle" in result
        assert "end" in result
        assert "[[Category:" not in result

    def test_remove_categories_with_empty_category(self):
        """A category link with an empty category name is still removed."""
        text = "Content [[Category:]] more"
        result = remove_categories(text)

        # Empty category name should still be caught
        assert "Content" in result
        assert "more" in result
