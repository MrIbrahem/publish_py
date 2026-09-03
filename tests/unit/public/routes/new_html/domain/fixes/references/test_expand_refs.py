"""
Unit tests for src/main_app/public/routes/new_html/domain/fixes/references/expand_refs.py module.

Functions to test: expand_text_refs

Ported from the PHP suite ``ExpendRefsTest`` (FixRefs\\Tests\\WikiTextFixes).
"""

from __future__ import annotations

from src.main_app.public.routes.new_html.domain.fixes.references.expand_refs import (
    expand_text_refs,
)


class TestExpandTextRefs:
    """Tests for the `expand_text_refs` function of the `expand_refs` module."""

    def test_refs_expand_works_with_short_ref_and_full_in_alltext(self):
        """A short ref in `first` is expanded using the full ref found in `alltext`."""
        first = 'Lead text <ref name="cite" />'
        alltext = 'Full article <ref name="cite">Full citation</ref>'

        result = expand_text_refs(first, alltext)

        assert '<ref name="cite">Full citation</ref>' in result
        assert '<ref name="cite" />' not in result

    def test_refs_expand_works_with_full_ref_already_in_first(self):
        """A short ref is left alone when its full ref is already present in `first`."""
        first = 'Lead text <ref name="cite">Citation</ref> <ref name="cite" />'
        alltext = 'Full article <ref name="cite">Citation</ref>'

        result = expand_text_refs(first, alltext)

        assert '<ref name="cite">Citation</ref>' in result
        assert '<ref name="cite" />' in result

    def test_refs_expand_works_with_no_matching_full_ref(self):
        """A short ref with no matching full ref anywhere is left unchanged."""
        first = 'Lead text <ref name="orphan" />'
        alltext = 'Full article <ref name="other">Other citation</ref>'

        result = expand_text_refs(first, alltext)

        assert '<ref name="orphan" />' in result

    def test_refs_expand_works_with_empty_alltext(self):
        """An empty `alltext` falls back to using `first` as the source of full refs."""
        first = 'Lead text <ref name="cite" />'
        alltext = ""

        result = expand_text_refs(first, alltext)

        assert "Lead text" in result

    def test_refs_expand_works_with_multiple_short_refs(self):
        """Several distinct short refs are each expanded from their own full ref."""
        first = '<ref name="a" /> <ref name="b" /> <ref name="c" />'
        alltext = '<ref name="a">Cite A</ref> <ref name="b">Cite B</ref> <ref name="c">Cite C</ref>'

        result = expand_text_refs(first, alltext)

        assert '<ref name="a">Cite A</ref>' in result
        assert '<ref name="b">Cite B</ref>' in result
        assert '<ref name="c">Cite C</ref>' in result

    def test_refs_expand_works_with_no_short_refs(self):
        """Text containing only a full ref is returned unchanged."""
        first = 'Lead text <ref name="full">Full citation</ref>'
        alltext = 'Full article <ref name="full">Full citation</ref>'

        result = expand_text_refs(first, alltext)

        assert result == first

    def test_refs_expand_works_with_empty_first(self):
        """An empty `first` produces an empty result."""
        result = expand_text_refs("", "Some alltext")

        assert result == ""

    def test_refs_expand_works_with_short_ref_without_name(self):
        """A nameless short ref (`<ref />`) is handled gracefully without crashing."""
        first = "Text <ref /> without name"
        alltext = "Full <ref>Citation</ref>"

        result = expand_text_refs(first, alltext)

        assert "Text" in result

    def test_refs_expand_works_preserves_other_content(self):
        """Surrounding lead paragraph text is preserved around the expanded ref."""
        first = 'Lead paragraph. <ref name="cite" /> More content.'
        alltext = '<ref name="cite">Full citation</ref>'

        result = expand_text_refs(first, alltext)

        assert "Lead paragraph." in result
        assert "More content." in result
        assert '<ref name="cite">Full citation</ref>' in result

    def test_refs_expand_works_with_mixed_refs(self):
        """A short ref with a full definition is expanded while an orphan one is untouched."""
        first = '<ref name="has_full" /> and <ref name="no_full" />'
        alltext = '<ref name="has_full">Citation</ref>'

        result = expand_text_refs(first, alltext)

        assert '<ref name="has_full">Citation</ref>' in result
        assert '<ref name="no_full" />' in result

    def test_refs_expand_works_with_complex_citation(self):
        """A full ref containing a citation template is inserted verbatim."""
        first = 'Text <ref name="complex" />'
        alltext = '<ref name="complex">{{cite journal|author=Smith|title=Paper|year=2020}}</ref>'

        result = expand_text_refs(first, alltext)

        assert "{{cite journal|author=Smith|title=Paper|year=2020}}" in result
        assert '<ref name="complex" />' not in result

    def test_refs_expand_works_with_whitespace_variations(self):
        """A full ref definition with extra internal whitespace is matched and inserted."""
        first = 'Text <ref name="cite"  />'
        alltext = '<ref name="cite" >Full citation</ref>'

        result = expand_text_refs(first, alltext)

        assert '<ref name="cite" >Full citation</ref>' in result

    def test_refs_expand_works_does_not_replace_if_full_ref_exists(self):
        """The short ref is left in place, and no new content is inserted, when a full ref
        for the same name already exists in `first` (even a differently worded one)."""
        first = '<ref name="cite">Already here</ref> and <ref name="cite" />'
        alltext = '<ref name="cite">Different citation</ref>'

        result = expand_text_refs(first, alltext)

        assert '<ref name="cite">Already here</ref>' in result
        assert '<ref name="cite" />' in result
        assert "Different citation" not in result

    def test_refs_expand_works_with_special_characters_in_name(self):
        """A ref name containing a colon is matched correctly."""
        first = 'Text <ref name="author_2020:page_5" />'
        alltext = '<ref name="author_2020:page_5">Citation content</ref>'

        result = expand_text_refs(first, alltext)

        assert '<ref name="author_2020:page_5">Citation content</ref>' in result

    def test_refs_expand_works_with_multiple_occurrences_of_same_short_ref(self):
        """Every occurrence of the same short ref name is replaced with the full ref."""
        first = '<ref name="cite" /> text <ref name="cite" /> more <ref name="cite" />'
        alltext = '<ref name="cite">Full citation</ref>'

        result = expand_text_refs(first, alltext)

        count = result.count('<ref name="cite">Full citation</ref>')
        assert count == 3

    def test_refs_expand_works_with_nested_content(self):
        """Nested HTML-like tags inside the expanded full ref are preserved."""
        first = 'Text <ref name="nested" />'
        alltext = '<ref name="nested">Citation with <span>nested</span> content</ref>'

        result = expand_text_refs(first, alltext)

        assert "<span>nested</span>" in result
