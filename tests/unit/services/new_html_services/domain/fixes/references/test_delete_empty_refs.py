"""
Unit tests for src/main_app/services/new_html_services/domain/fixes/references/delete_empty_refs.py module.

Functions to test: del_empty_refs

Ported from the PHP suite ``DelMtRefsTest`` (FixRefs\\Tests\\WikiTextFixes).
"""

from __future__ import annotations

from src.main_app.services.new_html_services.domain.fixes.references.delete_empty_refs import (
    del_empty_refs,
)


class TestDelEmptyRefs:
    """Tests for the `del_empty_refs` function of the `delete_empty_refs` module."""

    def test_basic(self):
        text = """[[File:Afatinib mechanism.svg|thumb|left|upright=2|Afatinib [[covalent]]ly binds to [[cysteine]] number 797 of the [[epidermal growth factor receptor]] (EGFR) via a [[Michael addition reaction|Michael addition]] ([[IC50|IC<sub>50</sub>]] = 0.5 [[nanomolar|nM]]).<ref>Schubert-Zsilavecz, M, Wurglics, M, ''Neue Arzneimittel Frühjahr 2013''. {{in lang|de}}</ref>]]<ref name="not_exists_ref_should_be_deleted"/>"""
        result = del_empty_refs(text)

    def test_basic2(self):
        text = """Afatinib [[covalent]]ly binds to [[cysteine]] number 797 of the [[epidermal growth factor receptor]] (EGFR) via a [[Michael addition reaction|Michael addition]] ([[IC50|IC<sub>50</sub>]] = 0.5 [[nanomolar|nM]]).<ref name="AHFS2022"/><ref>Schubert-Zsilavecz, M, Wurglics, M, ''Neue Arzneimittel Frühjahr 2013''. {{in lang|de}}</ref><ref name="not_exists_ref_should_be_deleted"/><ref name=AHFS2022>Afatinib Monograph for Professionals</ref>"""

        result = del_empty_refs(text)

        assert '<ref name="not_exists_ref_should_be_deleted"/>' not in result

        assert (
            result
            == """Afatinib [[covalent]]ly binds to [[cysteine]] number 797 of the [[epidermal growth factor receptor]] (EGFR) via a [[Michael addition reaction|Michael addition]] ([[IC50|IC<sub>50</sub>]] = 0.5 [[nanomolar|nM]]).<ref name="AHFS2022"/><ref>Schubert-Zsilavecz, M, Wurglics, M, ''Neue Arzneimittel Frühjahr 2013''. {{in lang|de}}</ref><ref name=AHFS2022>Afatinib Monograph for Professionals</ref>"""
        )

    def test_del_empty_refs_with_valid_short_ref(self):
        """A short ref stays untouched when its full ref definition exists elsewhere."""
        text = '<ref name="test">Full citation</ref> Some text <ref name="test" />'
        result = del_empty_refs(text)

        assert '<ref name="test">Full citation</ref>' in result
        assert '<ref name="test" />' in result

    def test_del_empty_refs_with_orphan_short_ref(self):
        """A short ref with no matching full ref is removed entirely."""
        text = 'Some text <ref name="orphan" /> without full reference'
        result = del_empty_refs(text)

        assert '<ref name="orphan" />' not in result
        assert "Some text" in result
        assert "without full reference" in result

    def test_del_empty_refs_replaces_with_full_ref(self):
        """A short ref appearing before its full definition is replaced with the full ref."""
        text = 'Text <ref name="cite" /> more text. Later: <ref name="cite">Full content</ref>'
        result = del_empty_refs(text)

        assert '<ref name="cite">Full content</ref>' in result

    def test_del_empty_refs_with_multiple_short_refs(self):
        """Only the short refs whose name lacks a full definition are removed."""
        text = '<ref name="a">Full A</ref> <ref name="a" /> <ref name="b" /> <ref name="a" />'
        result = del_empty_refs(text)

        assert '<ref name="a">Full A</ref>' in result
        assert '<ref name="b" />' not in result

    def test_del_empty_refs_with_no_short_refs(self):
        """Text made up only of full refs is returned unchanged."""
        text = '<ref name="one">Citation 1</ref> <ref name="two">Citation 2</ref>'
        result = del_empty_refs(text)

        assert result == text

    def test_del_empty_refs_with_no_refs(self):
        """Text without any refs is returned unchanged."""
        text = "Plain text without any references"
        result = del_empty_refs(text)

        assert result == text

    def test_del_empty_refs_with_empty_text(self):
        """Empty input returns empty output."""
        result = del_empty_refs("")

        assert result == ""

    def test_del_empty_refs_preserves_full_refs(self):
        """Full ref definitions are always preserved."""
        text = '<ref name="full1">Citation 1</ref> <ref name="full2">Citation 2</ref>'
        result = del_empty_refs(text)

        assert '<ref name="full1">Citation 1</ref>' in result
        assert '<ref name="full2">Citation 2</ref>' in result

    def test_del_empty_refs_does_not_duplicate_full_ref(self):
        """A full ref already present in the text is not duplicated when expanding a short ref."""
        text = '<ref name="cite">Full citation</ref> Text <ref name="cite" />'
        result = del_empty_refs(text)

        count = result.count('<ref name="cite">Full citation</ref>')
        assert count == 1

    def test_del_empty_refs_with_multiple_orphans(self):
        """All orphan short refs are removed."""
        text = '<ref name="orphan1" /> <ref name="orphan2" /> <ref name="orphan3" />'
        result = del_empty_refs(text)

        assert '<ref name="orphan1" />' not in result
        assert '<ref name="orphan2" />' not in result
        assert '<ref name="orphan3" />' not in result

    def test_del_empty_refs_with_mixed_refs(self):
        """A mix of valid and orphan short refs is handled correctly for each name."""
        text = '<ref name="valid">Full</ref> <ref name="valid" /> <ref name="invalid" />'
        result = del_empty_refs(text)

        assert '<ref name="valid">Full</ref>' in result
        assert '<ref name="valid" />' in result
        assert '<ref name="invalid" />' not in result

    def test_del_empty_refs_with_anonymous_refs(self):
        """An anonymous full ref is preserved while an orphan named short ref is removed."""
        text = 'Text <ref>Anonymous citation</ref> Text <ref name="named" />'
        result = del_empty_refs(text)

        assert "<ref>Anonymous citation</ref>" in result
        assert '<ref name="named" />' not in result

    def test_del_empty_refs_with_complex_names(self):
        """Ref names containing underscores and digits are matched correctly."""
        text = '<ref name="author_2020">Full citation</ref> <ref name="author_2020" />'
        result = del_empty_refs(text)

        assert '<ref name="author_2020">Full citation</ref>' in result
        assert '<ref name="author_2020" />' in result

    def test_del_empty_refs_replaces_short_ref_before_full_ref(self):
        """A short ref is replaced even when it appears before the full ref in the text."""
        text = 'Start <ref name="cite" /> middle. End <ref name="cite">Full content</ref>.'
        result = del_empty_refs(text)

        assert '<ref name="cite">Full content</ref>' in result

    def test_del_empty_refs_with_whitespace_in_short_ref(self):
        """Short refs with extra internal whitespace are still recognized."""
        text = '<ref name="test">Full</ref> <ref name="test"  />'
        result = del_empty_refs(text)

        assert '<ref name="test">Full</ref>' in result

    def test_del_empty_refs_with_nested_content(self):
        """Nested HTML-like tags inside a full ref definition are preserved."""
        text = '<ref name="complex">Citation with <span>nested</span> content</ref> <ref name="complex" />'
        result = del_empty_refs(text)

        assert "<span>nested</span>" in result
