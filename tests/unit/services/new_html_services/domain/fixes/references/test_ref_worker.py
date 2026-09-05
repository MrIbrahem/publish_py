"""
Unit tests for src/main_app/services/new_html_services/domain/fixes/references/ref_worker.py module.

Functions to test: check_one_cite, remove_bad_refs

Ported from the PHP suite ``RefWorkTest`` (FixRefs\\Tests\\WikiTextFixes).
"""

from __future__ import annotations

from src.main_app.services.new_html_services.domain.fixes.references.ref_worker import (
    check_one_cite,
    remove_bad_refs,
)

# ---------------------------------------------------------------------------
# Tests for check_one_cite
# ---------------------------------------------------------------------------


class TestCheckOneCite:
    """Tests for the `check_one_cite` function of the `ref_worker` module."""

    def test_check_one_cite_with_bad_doi(self):
        """A DOI prefix from the predatory-publisher list is flagged as bad."""
        cite = "<ref>{{cite journal|doi=10.5539/test}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_good_doi(self):
        """A DOI prefix not on the predatory-publisher list is not flagged."""
        cite = "<ref>{{cite journal|doi=10.1001/test}}</ref>"

        assert check_one_cite(cite) is False

    def test_check_one_cite_with_bad_journal(self):
        """A URL pointing to a known low-quality open-access journal domain is flagged."""
        cite = "<ref>{{cite journal|url=http://scirp.org/article}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_self_publisher(self):
        """A `publisher=` field naming a known self-publishing service is flagged."""
        cite = "<ref>{{cite book|publisher=Author House}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_create_space(self):
        """CreateSpace as a publisher is flagged."""
        cite = "<ref>{{cite book|publisher=CreateSpace}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_self_pub_url(self):
        """A URL pointing to a known self-publishing domain is flagged."""
        cite = "<ref>{{cite web|url=http://lulu.com/book}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_clean_citation(self):
        """A well-formed citation with no bad indicators is not flagged."""
        cite = "<ref>{{cite journal|title=Test|author=Smith|journal=Nature|year=2020}}</ref>"

        assert check_one_cite(cite) is False

    def test_check_one_cite_with_multiple_bad_patterns(self):
        """A citation matching more than one bad pattern is still flagged (once is enough)."""
        cite = "<ref>{{cite journal|doi=10.5539/test|url=http://scirp.org/article}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_omics_group(self):
        """A URL pointing to omicsonline.org is flagged."""
        cite = "<ref>{{cite journal|url=http://omicsonline.org/article}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_trafford_publishing(self):
        """Trafford Publishing as a publisher is flagged."""
        cite = "<ref>{{cite book|publisher=Trafford Publishing}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_i_universe(self):
        """iUniverse as a publisher is flagged."""
        cite = "<ref>{{cite book|publisher=iUniverse}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_x_libris(self):
        """XLibris as a publisher is flagged."""
        cite = "<ref>{{cite book|publisher=XLibris}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_edwin_mellen_press(self):
        """Edwin Mellen Press as a publisher is flagged."""
        cite = "<ref>{{cite book|publisher=Edwin Mellen Press}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_case_insensitive(self):
        """Publisher matching is case-insensitive."""
        cite = "<ref>{{cite book|publisher=AUTHOR HOUSE}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_hindawi(self):
        """A DOI prefix not on the bad list (e.g. Hindawi's 10.1155) is not flagged."""
        cite = "<ref>{{cite journal|doi=10.1155/test}}</ref>"
        # 10.1155 is not in the bad list, so should be false

        assert check_one_cite(cite) is False

    def test_check_one_cite_with_work_parameter(self):
        """A `work=` field (not just `publisher=`) naming a bad service is flagged."""
        cite = "<ref>{{cite|work=CreateSpace}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_url_in_text(self):
        """A bad domain appearing anywhere in the citation text is flagged."""
        cite = "<ref>Text with createspace.com in URL</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_multiple_doi_bad_prefixes(self):
        """Several distinct bad DOI prefixes are each individually flagged."""
        cite1 = "<ref>{{cite|doi=10.11648/test}}</ref>"
        cite2 = "<ref>{{cite|doi=10.1166/test}}</ref>"
        cite3 = "<ref>{{cite|doi=10.1234/test}}</ref>"

        assert check_one_cite(cite1) is True
        assert check_one_cite(cite2) is True
        assert check_one_cite(cite3) is True

    def test_check_one_cite_with_spaces_in_pattern(self):
        """Spaces around the `=`/`|`/`:` separator in `doi=` are tolerated."""
        cite = "<ref>{{cite|doi = 10.5539/test}}</ref>"

        assert check_one_cite(cite) is True

    def test_check_one_cite_with_nested_templates(self):
        """A bad DOI is detected even when the citation contains a nested template."""
        cite = "<ref>{{cite journal|title={{lang|en|Title}}|doi=10.5539/bad}}</ref>"

        assert check_one_cite(cite) is True


# ---------------------------------------------------------------------------
# Tests for remove_bad_refs
# ---------------------------------------------------------------------------


class TestRemoveBadRefs:
    """Tests for the `remove_bad_refs` function of the `ref_worker` module."""

    def test_remove_bad_refs_with_single_bad_ref(self):
        """A single bad ref is removed while surrounding text is preserved."""
        text = "Good text <ref>{{cite journal|doi=10.5539/bad}}</ref> more text"
        result = remove_bad_refs(text)

        assert "doi=10.5539/bad" not in result
        assert "Good text" in result
        assert "more text" in result

    def test_remove_bad_refs_with_multiple_bad_refs(self):
        """Every bad ref in the text is removed."""
        text = "<ref>{{cite|doi=10.5539/bad1}}</ref> text <ref>{{cite|url=http://scirp.org/x}}</ref>"
        result = remove_bad_refs(text)

        assert "doi=10.5539/bad1" not in result
        assert "scirp.org" not in result
        assert "text" in result

    def test_remove_bad_refs_preserves_good_refs(self):
        """A good ref is preserved while a bad ref alongside it is removed."""
        text = "<ref>{{cite journal|doi=10.1001/good}}</ref> <ref>{{cite|doi=10.5539/bad}}</ref>"
        result = remove_bad_refs(text)

        assert "doi=10.1001/good" in result
        assert "doi=10.5539/bad" not in result

    def test_remove_bad_refs_with_no_refs(self):
        """Text without any refs is returned unchanged."""
        text = "Plain text without references"
        result = remove_bad_refs(text)

        assert result == text

    def test_remove_bad_refs_with_empty_text(self):
        """Empty input returns empty output."""
        result = remove_bad_refs("")

        assert result == ""

    def test_remove_bad_refs_with_named_ref(self):
        """A bad ref with a `name=` attribute is still removed."""
        text = '<ref name="bad">{{cite|doi=10.5539/test}}</ref>'
        result = remove_bad_refs(text)

        assert "doi=10.5539/test" not in result

    def test_remove_bad_refs_with_mixed_refs(self):
        """Good refs on either side of a bad ref are both preserved."""
        text = "<ref>Good ref</ref> <ref>{{cite|doi=10.5539/bad}}</ref> <ref>Another good</ref>"
        result = remove_bad_refs(text)

        assert "<ref>Good ref</ref>" in result
        assert "<ref>Another good</ref>" in result
        assert "doi=10.5539/bad" not in result

    def test_remove_bad_refs_with_complex_citations(self):
        """A bad ref with several other fields is still removed as a whole."""
        text = '<ref name="complex">{{cite journal|author=Smith|title=Test|doi=10.5539/bad|year=2020}}</ref>'
        result = remove_bad_refs(text)

        assert "doi=10.5539/bad" not in result

    def test_remove_bad_refs_preserves_text_structure(self):
        """Paragraph breaks and surrounding whitespace are preserved when a bad ref is removed."""
        text = "Paragraph 1.\n\n<ref>{{cite|doi=10.5539/bad}}</ref>\n\nParagraph 2."
        result = remove_bad_refs(text)

        assert "Paragraph 1.\n\n" in result
        assert "\n\nParagraph 2." in result
        assert "doi=10.5539/bad" not in result

    def test_remove_bad_refs_with_all_good_refs(self):
        """Text where every ref is good is returned unchanged."""
        text = "<ref>{{cite journal|doi=10.1001/test}}</ref> <ref>Good citation</ref>"
        result = remove_bad_refs(text)

        assert result == text
