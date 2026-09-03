"""
Unit tests for src/main_app/public/routes/new_html/domain/fixes/structure/fix_language_links.py module.

Functions to test: remove_lang_links, is_valid_lang_code

Ported from the PHP suite ``FixLangsLinksTest`` (FixRefs\\Tests\\WikiTextFixes).
"""

from __future__ import annotations

from src.main_app.public.routes.new_html.domain.fixes.structure.fix_language_links import (
    LANG_CODES,
    is_valid_lang_code,
    remove_lang_links,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

# Full list of Wikipedia interwiki language codes, mirrored from the PHP
# suite's ALL_WIKI_LANG_CODES constant, used to check the regex pattern
# accepts every known code.
ALL_WIKI_LANG_CODES = sorted(LANG_CODES)


# ---------------------------------------------------------------------------
# Tests for is_valid_lang_code
# ---------------------------------------------------------------------------


class TestIsValidLangCode:
    """Tests for the `is_valid_lang_code` function of the `fix_language_links` module."""

    def test_all_wiki_lang_codes_are_valid(self):
        """Every known Wikipedia language code matches the validity pattern."""
        for code in ALL_WIKI_LANG_CODES:
            assert is_valid_lang_code(code), f"Language code '{code}' should be valid"

    def test_invalid_lang_codes(self):
        """A variety of malformed codes are all rejected."""
        invalid_codes = [
            "X",  # Too short (single uppercase)
            "E",  # Single letter
            "1",  # Number
            "en1",  # Contains number
            "EN",  # Uppercase
            "En",  # Mixed case
            "-en",  # Starts with hyphen
            "en-",  # Ends with hyphen
            "",  # Empty string
            "test_",  # Contains underscore
            "en.test",  # Contains dot
            "en space",  # Contains space
        ]

        for code in invalid_codes:
            assert not is_valid_lang_code(code), f"Code '{code}' should be invalid"

    def test_is_valid_lang_code_with_single_character(self):
        """A single character is invalid; the minimum length is two."""
        assert is_valid_lang_code("e") is False
        assert is_valid_lang_code("x") is False
        assert is_valid_lang_code("a") is False

    def test_is_valid_lang_code_with_numbers_in_code(self):
        """Codes containing digits anywhere are rejected."""
        assert is_valid_lang_code("en1") is False
        assert is_valid_lang_code("2de") is False
        assert is_valid_lang_code("e3n") is False
        assert is_valid_lang_code("en-123") is False

    def test_is_valid_lang_code_with_multiple_hyphens(self):
        """Multiple hyphen-separated segments are valid, but stray/edge hyphens are not."""
        assert is_valid_lang_code("zh-min-nan") is True
        assert is_valid_lang_code("en--de") is False  # Double hyphen
        assert is_valid_lang_code("en-") is False  # Trailing hyphen
        assert is_valid_lang_code("-en") is False  # Leading hyphen

    def test_is_valid_lang_code_with_two_character_code(self):
        """The two-character boundary case is valid."""
        assert is_valid_lang_code("en") is True
        assert is_valid_lang_code("de") is True
        assert is_valid_lang_code("fr") is True
        assert is_valid_lang_code("ja") is True

    def test_is_valid_lang_code_with_very_long_hyphenated_code(self):
        """Longer hyphenated codes are valid."""
        assert is_valid_lang_code("zh-min-nan") is True
        assert is_valid_lang_code("be-tarask") is True
        assert is_valid_lang_code("roa-rup") is True

    def test_is_valid_lang_code_with_special_characters(self):
        """Codes with underscores, dots, spaces, or symbols are rejected."""
        assert is_valid_lang_code("en_us") is False
        assert is_valid_lang_code("en.us") is False
        assert is_valid_lang_code("en us") is False
        assert is_valid_lang_code("en@us") is False
        assert is_valid_lang_code("en:us") is False


# ---------------------------------------------------------------------------
# Tests for remove_lang_links
# ---------------------------------------------------------------------------


class TestRemoveLangLinks:
    """Tests for the `remove_lang_links` function of the `fix_language_links` module."""

    def test_remove_lang_links_with_single_link(self):
        """A single interwiki language link is removed while surrounding text remains."""
        text = "Article content [[en:Article]] more text"
        result = remove_lang_links(text)

        assert "[[en:Article]]" not in result
        assert "Article content" in result
        assert "more text" in result

    def test_remove_lang_links_with_multiple_links(self):
        """Several interwiki language links are all removed."""
        text = "[[en:English Article]] content [[de:German Article]] [[fr:French Article]]"
        result = remove_lang_links(text)

        assert "[[en:English Article]]" not in result
        assert "[[de:German Article]]" not in result
        assert "[[fr:French Article]]" not in result
        assert "content" in result

    def test_remove_lang_links_preserves_normal_links(self):
        """Ordinary article wikilinks are preserved while a language link is removed."""
        text = "[[Normal link]] [[en:Language link]] [[Another link]]"
        result = remove_lang_links(text)

        assert "[[Normal link]]" in result
        assert "[[Another link]]" in result
        assert "[[en:Language link]]" not in result

    def test_remove_lang_links_with_no_language_links(self):
        """Text without any language links is returned unchanged."""
        text = "Text without language links [[Article]] more text"
        result = remove_lang_links(text)

        assert result == text

    def test_remove_lang_links_with_empty_text(self):
        """Empty input returns empty output."""
        result = remove_lang_links("")

        assert result == ""

    def test_remove_lang_links_with_various_languages(self):
        """Language links using non-Latin article titles are all removed."""
        text = "[[ar:مقالة]] [[ja:記事]] [[zh:文章]] [[ru:Статья]]"
        result = remove_lang_links(text)

        assert "[[ar:" not in result
        assert "[[ja:" not in result
        assert "[[zh:" not in result
        assert "[[ru:" not in result

    def test_remove_lang_links_at_end_of_article(self):
        """Trailing language links at the end of an article are all removed."""
        text = "Article content.\n\n[[en:English]]\n[[de:Deutsch]]\n[[fr:Français]]"
        result = remove_lang_links(text)

        assert "Article content." in result
        assert "[[en:" not in result
        assert "[[de:" not in result
        assert "[[fr:" not in result

    def test_remove_lang_links_with_complex_article_names(self):
        """A language link whose title contains spaces and parentheses is removed."""
        text = "[[en:Article with spaces and (parentheses)]] content"
        result = remove_lang_links(text)

        assert "[[en:Article with spaces and (parentheses)]]" not in result
        assert "content" in result

    def test_remove_lang_links_preserves_categories(self):
        """Category links surrounding a language link are preserved."""
        text = "[[Category:Test]] [[en:Article]] [[Category:Another]]"
        result = remove_lang_links(text)

        assert "[[Category:Test]]" in result
        assert "[[Category:Another]]" in result
        assert "[[en:Article]]" not in result

    def test_remove_lang_links_with_special_characters(self):
        """Language links with accented and underscore-separated titles are removed."""
        text = "[[es:Artículo con acentos]] [[de:Artikel_mit_Unterstrichen]]"
        result = remove_lang_links(text)

        assert "[[es:" not in result
        assert "[[de:" not in result

    def test_remove_lang_links_inline_with_text(self):
        """Language links interspersed with plain text throughout are all removed."""
        text = "Start [[en:Article]] middle [[fr:Article]] end"
        result = remove_lang_links(text)

        assert "Start" in result
        assert "middle" in result
        assert "end" in result
        assert "[[en:" not in result
        assert "[[fr:" not in result

    def test_remove_lang_links_with_duplicates(self):
        """Repeated links to the same language are both removed."""
        text = "[[en:Article]] content [[en:Article]]"
        result = remove_lang_links(text)

        assert "[[en:Article]]" not in result
        assert "content" in result

    def test_remove_lang_links_preserves_templates(self):
        """Templates before and after a language link are left untouched."""
        text = "{{Template}} [[en:Article]] {{Another}}"
        result = remove_lang_links(text)

        assert "{{Template}}" in result
        assert "{{Another}}" in result
        assert "[[en:Article]]" not in result

    def test_remove_lang_links_with_newlines(self):
        """A language link surrounded by newlines is removed, preserving the newlines."""
        text = "Content\n[[en:Article]]\nMore content"
        result = remove_lang_links(text)

        assert "Content\n" in result
        assert "More content" in result
        assert "[[en:Article]]" not in result

    def test_remove_lang_links_with_mixed_content(self):
        """A mix of normal links, templates, categories, and language links is handled correctly."""
        text = "[[Article]] text [[en:Lang]] {{Template}} [[Category:Cat]] [[de:Sprache]]"
        result = remove_lang_links(text)

        assert "[[Article]]" in result
        assert "{{Template}}" in result
        assert "[[Category:Cat]]" in result
        assert "[[en:" not in result
        assert "[[de:" not in result

    def test_remove_lang_links_with_underscores_and_spaces(self):
        """Language link titles with underscores or spaces are removed."""
        text = "[[en:Article_with_underscores]] [[de:Article with spaces]]"
        result = remove_lang_links(text)

        assert "[[en:Article_with_underscores]]" not in result
        assert "[[de:Article with spaces]]" not in result

    def test_remove_lang_links_with_section_links(self):
        """A language link that includes a `#Section` fragment is removed."""
        text = "[[en:Article#Section]] content"
        result = remove_lang_links(text)

        assert "[[en:Article#Section]]" not in result
        assert "content" in result

    def test_remove_lang_links_preserves_file_links(self):
        """`File:` links are never mistaken for language links."""
        text = "[[File:Image.jpg]] [[en:Article]] [[Category:Test]]"
        result = remove_lang_links(text)

        assert "[[File:Image.jpg]]" in result
        assert "[[Category:Test]]" in result
        assert "[[en:Article]]" not in result

    def test_remove_lang_links_with_hyphenated_codes(self):
        """Hyphenated language codes (e.g. be-tarask) are matched and removed."""
        text = "[[be-tarask:Артыкул]] [[zh-min-nan:Bûn-chiuⁿ]] [[roa-rup:Articlu]]"
        result = remove_lang_links(text)

        assert "[[be-tarask:" not in result
        assert "[[zh-min-nan:" not in result
        assert "[[roa-rup:" not in result

    def test_remove_lang_links_preserves_short_invalid_codes(self):
        """Codes that don't match the lowercase 2+-letter pattern are left as ordinary links."""
        # Actually, 'xy' and 'zz' match the pattern (2+ lowercase letters)
        # so they WILL be removed as they're valid lang codes
        text = "[[X:Article]] [[12:Number]] [[EN:Uppercase]] [[e:Single]]"
        result = remove_lang_links(text)

        # These should remain (don't match the pattern)
        assert "[[X:Article]]" in result  # Uppercase
        assert "[[12:Number]]" in result  # Starts with number
        assert "[[EN:Uppercase]]" in result  # Uppercase
        assert "[[e:Single]]" in result  # Single char

    def test_remove_lang_links_with_simple_code(self):
        """The special `simple:` language code is recognized and removed."""
        text = "[[simple:Basic English article]] content"
        result = remove_lang_links(text)

        assert "[[simple:" not in result
        assert "content" in result

    def test_remove_lang_links_with_pipe_display_text(self):
        """A language link with piped display text is removed as a whole."""
        text = "[[en:Article|Display Text]] content"
        result = remove_lang_links(text)

        assert "[[en:Article|Display Text]]" not in result
        assert "content" in result

    def test_remove_lang_links_consecutive_without_space(self):
        """Consecutive language links with no separating whitespace are all removed."""
        text = "content[[en:Article]][[de:Artikel]][[fr:Article]]text"
        result = remove_lang_links(text)

        assert "[[en:Article]]" not in result
        assert "[[de:Artikel]]" not in result
        assert "[[fr:Article]]" not in result
        assert "content" in result
        assert "text" in result

    def test_remove_lang_links_with_colon_in_article_name(self):
        """A language link whose title itself contains a namespace-style colon is removed."""
        text = "[[en:User:Example]] [[de:Wikipedia:Featured article]]"
        result = remove_lang_links(text)

        assert "[[en:User:Example]]" not in result
        assert "[[de:Wikipedia:Featured article]]" not in result

    def test_remove_lang_links_preserves_whitespace(self):
        """Whitespace/newlines around a removed language link are preserved."""
        text = "Line 1\n[[en:Article]]\nLine 2"
        result = remove_lang_links(text)

        assert "Line 1\n" in result
        assert "\nLine 2" in result
        assert "[[en:Article]]" not in result

    def test_remove_lang_links_at_very_start_of_text(self):
        """A language link as the very first thing in the text is removed."""
        text = "[[en:Article]] followed by content"
        result = remove_lang_links(text)

        assert "[[en:Article]]" not in result
        assert "followed by content" in result

    def test_remove_lang_links_at_very_end_of_text(self):
        """A language link as the very last thing in the text is removed."""
        text = "content before [[en:Article]]"
        result = remove_lang_links(text)

        assert "[[en:Article]]" not in result
        assert "content before" in result

    def test_remove_lang_links_only_language_links(self):
        """Text consisting solely of language links becomes empty."""
        text = "[[en:Article]][[de:Artikel]][[fr:Article]]"
        result = remove_lang_links(text)

        assert result == ""

    def test_remove_lang_links_does_not_match_uppercase(self):
        """Uppercase-prefixed links are not treated as language links and remain untouched."""
        text = "[[EN:Article]] [[De:Artikel]] [[FR:Article]]"
        result = remove_lang_links(text)

        # All should remain because they don't match the lowercase pattern
        assert "[[EN:Article]]" in result
        assert "[[De:Artikel]]" in result
        assert "[[FR:Article]]" in result

    def test_remove_lang_links_with_unicode_in_article_name(self):
        """Language links with fully Unicode article titles are removed."""
        text = "[[ja:日本語の記事]] [[ar:مقالة عربية]] [[ru:Русская статья]] [[zh:中文文章]]"
        result = remove_lang_links(text)

        assert "[[ja:日本語の記事]]" not in result
        assert "[[ar:مقالة عربية]]" not in result
        assert "[[ru:Русская статья]]" not in result
        assert "[[zh:中文文章]]" not in result

    def test_remove_lang_links_with_complex_mixed_content(self):
        """A realistic article snippet mixing every link/template type is handled correctly."""
        text = (
            "== Section ==\n"
            "This is content with [[internal link]] and [[en:English article]].\n\n"
            "{{template|param=value}}\n"
            "More text [[Category:Test Category]] and [[de:Deutscher Artikel]].\n\n"
            "* List item with [[fr:Article français]]\n"
            "* Another item\n\n"
            "[[File:Example.jpg|thumb|Caption]]\n\n"
            "[[zh-min-nan:Bûn-chiuⁿ]]"
        )
        result = remove_lang_links(text)

        # Should preserve all non-language-link content
        assert "[[internal link]]" in result
        assert "{{template|param=value}}" in result
        assert "[[Category:Test Category]]" in result
        assert "[[File:Example.jpg|thumb|Caption]]" in result

        # Should remove all language links
        assert "[[en:English article]]" not in result
        assert "[[de:Deutscher Artikel]]" not in result
        assert "[[fr:Article français]]" not in result
        assert "[[zh-min-nan:Bûn-chiuⁿ]]" not in result

    def test_remove_lang_links_with_trailing_spaces(self):
        """Extra whitespace around a language link doesn't prevent its removal."""
        text = "Before  [[en:Article]]  After"
        result = remove_lang_links(text)

        assert "[[en:Article]]" not in result
        assert "Before" in result
        assert "After" in result

    def test_remove_lang_links_regression_all_known_codes(self):
        """Regression test: every hyphenated Wikipedia language code is properly removed."""
        problematic_codes = [
            "be-tarask",
            "bat-smg",
            "cbk-zam",
            "fiu-vro",
            "map-bms",
            "nds-nl",
            "roa-rup",
            "roa-tara",
            "zh-classical",
            "zh-min-nan",
            "zh-yue",
        ]

        for code in problematic_codes:
            text = f"Content [[{code}:Article]] more text"
            result = remove_lang_links(text)

            assert f"[[{code}:" not in result, f"Failed to remove language code: {code}"
            assert "Content" in result
            assert "more text" in result

    def test_remove_lang_links_does_not_remove_image_links(self):
        """`Image:`/`File:` links are never accidentally removed as language links."""
        text = "[[Image:Test.jpg]] [[File:Another.png]] [[en:Article]]"
        result = remove_lang_links(text)

        assert "[[Image:Test.jpg]]" in result
        assert "[[File:Another.png]]" in result
        assert "[[en:Article]]" not in result

    def test_remove_lang_links_with_parentheses_and_brackets(self):
        """A language link whose title has complex punctuation is removed without error."""
        text = "[[en:Article (disambiguation)]] [[de:Begriff [Erklärung]]]"
        result = remove_lang_links(text)

        assert "[[en:Article (disambiguation)]]" not in result
        # Note: [Erklärung] inside might cause parsing quirks, but removal
        # of the outer en: link should still succeed.

    def test_remove_lang_links_with_query_parameters(self):
        """Language link titles containing query-like characters are removed."""
        text = "[[en:Article?action=edit]] [[de:Artikel&param=value]]"
        result = remove_lang_links(text)

        assert "[[en:Article?action=edit]]" not in result
        assert "[[de:Artikel&param=value]]" not in result
