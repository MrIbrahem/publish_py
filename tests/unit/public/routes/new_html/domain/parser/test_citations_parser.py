# ruff: noqa: F401
"""
Unit tests for src/main_app/public/routes/new_html/domain/parser/citations_parser.py module.

Functions to test: get_citations, get_full_refs, get_short_refs
"""

from src.main_app.public.routes.new_html.domain.parser.citations_parser import (
    get_citations,
    get_full_refs,
    get_short_refs,
)


class TestGetCitations:
    """
    Tests for get_citations function
    """

    def test_single_full_ref_no_name(self):
        text = "Some text<ref>A basic citation</ref> more text"
        result = get_citations(text)

        assert len(result) == 1
        assert result[0]["content"] == "A basic citation"
        assert result[0]["tag"] == "<ref>A basic citation</ref>"
        assert result[0]["name"] == ""

    def test_single_full_ref_with_name(self):
        text = '<ref name="smith2020">Smith, J. (2020)</ref>'
        result = get_citations(text)

        assert len(result) == 1
        assert result[0]["content"] == "Smith, J. (2020)"
        assert result[0]["name"] == "smith2020"
        assert result[0]["options"]["name"] == "smith2020"
        assert result[0]["tag"] == text

    def test_multiple_full_refs(self):
        text = "Text<ref>First</ref> more<ref>Second</ref>"
        result = get_citations(text)

        assert len(result) == 2
        assert result[0]["content"] == "First"
        assert result[1]["content"] == "Second"

    def test_excludes_self_closing_refs(self):
        text = 'Text<ref name="a">Full ref</ref> and<ref name="a" /> a short ref'
        result = get_citations(text)

        assert len(result) == 1
        assert result[0]["content"] == "Full ref"
        assert result[0]["name"] == "a"

    def test_no_refs_returns_empty_list(self):
        result = get_citations("Just some plain text without any refs")

        assert result == []

    def test_empty_text_returns_empty_list(self):
        result = get_citations("")

        assert result == []

    def test_ref_with_extra_attributes(self):
        text = '<ref name="foo" group="note">Some content</ref>'
        result = get_citations(text)

        assert len(result) == 1
        assert result[0]["name"] == "foo"
        assert result[0]["options"]["name"] == "foo"
        assert result[0]["options"]["group"] == "note"

    def test_ref_name_is_stripped(self):
        text = '<ref name=" spaced ">Content</ref>'
        result = get_citations(text)

        assert len(result) == 1
        assert result[0]["name"] == "spaced"

    def test_nested_markup_inside_ref(self):
        text = '<ref>See [[Some Page|the page]] for {{cite web|url=example.com}} details</ref>'
        result = get_citations(text)

        assert len(result) == 1
        assert "[[Some Page|the page]]" in result[0]["content"]
        assert "{{cite web|url=example.com}}" in result[0]["content"]

    def test_multiline_ref_content(self):
        text = "<ref>Line one\nLine two\nLine three</ref>"
        result = get_citations(text)

        assert len(result) == 1
        assert result[0]["content"] == "Line one\nLine two\nLine three"

    def test_duplicate_names_both_returned(self):
        text = '<ref name="dup">First</ref> text <ref name="dup">Second</ref>'
        result = get_citations(text)

        assert len(result) == 2
        assert [c["content"] for c in result] == ["First", "Second"]
        assert all(c["name"] == "dup" for c in result)


class TestGetFullRefs:
    """
    Tests for get_full_refs function
    """

    def test_single_named_ref(self):
        text = '<ref name="smith2020">Smith, J. (2020)</ref>'
        result = get_full_refs(text)

        assert result == {"smith2020": '<ref name="smith2020">Smith, J. (2020)</ref>'}

    def test_multiple_named_refs(self):
        text = '<ref name="a">First</ref> text <ref name="b">Second</ref>'
        result = get_full_refs(text)

        assert set(result.keys()) == {"a", "b"}
        assert result["a"] == '<ref name="a">First</ref>'
        assert result["b"] == '<ref name="b">Second</ref>'

    def test_unnamed_refs_excluded(self):
        text = '<ref>No name here</ref><ref name="named">Has name</ref>'
        result = get_full_refs(text)

        assert list(result.keys()) == ["named"]

    def test_self_closing_refs_excluded(self):
        text = '<ref name="full">Full ref</ref><ref name="short" />'
        result = get_full_refs(text)

        assert list(result.keys()) == ["full"]

    def test_no_refs_returns_empty_dict(self):
        result = get_full_refs("Plain text, no refs at all")

        assert result == {}

    def test_empty_text_returns_empty_dict(self):
        result = get_full_refs("")

        assert result == {}

    def test_duplicate_names_last_occurrence_wins(self):
        text = '<ref name="dup">First</ref> text <ref name="dup">Second</ref>'
        result = get_full_refs(text)

        assert result == {"dup": '<ref name="dup">Second</ref>'}


class TestGetShortRefs:
    """
    Tests for get_short_refs function
    """

    def test_single_short_ref(self):
        text = '<ref name="smith2020" />'
        result = get_short_refs(text)

        assert len(result) == 1
        assert result[0]["name"] == "smith2020"
        assert result[0]["content"] == ""
        assert result[0]["tag"] == '<ref name="smith2020" />'

    def test_multiple_short_refs(self):
        text = 'Text<ref name="a"/> more<ref name="b" />'
        result = get_short_refs(text)

        assert len(result) == 2
        assert {c["name"] for c in result} == {"a", "b"}
        assert all(c["content"] == "" for c in result)

    def test_excludes_full_refs(self):
        text = '<ref name="full">Full content</ref><ref name="short" />'
        result = get_short_refs(text)

        assert len(result) == 1
        assert result[0]["name"] == "short"

    def test_no_refs_returns_empty_list(self):
        result = get_short_refs("No refs in this text")

        assert result == []

    def test_empty_text_returns_empty_list(self):
        result = get_short_refs("")

        assert result == []

    def test_short_ref_without_name(self):
        text = "<ref />"
        result = get_short_refs(text)

        assert len(result) == 1
        assert result[0]["name"] == ""
        assert result[0]["content"] == ""

    def test_short_ref_name_is_stripped(self):
        text = '<ref name=" spaced " />'
        result = get_short_refs(text)

        assert len(result) == 1
        assert result[0]["name"] == "spaced"

    def test_short_ref_with_extra_attributes(self):
        text = '<ref name="foo" group="note" />'
        result = get_short_refs(text)

        assert len(result) == 1
        assert result[0]["options"]["name"] == "foo"
        assert result[0]["options"]["group"] == "note"

    def test_no_space_before_self_close(self):
        text = '<ref name="tight"/>'
        result = get_short_refs(text)

        assert len(result) == 1
        assert result[0]["name"] == "tight"
