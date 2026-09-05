"""
Unit tests for src/main_app/services/new_html_services/domain/fixes/templates/delete_templates.py module.

Functions to test: remove_templates, remove_lead_templates

Ported from the PHP suite ``DelTempsTest`` (FixRefs\\Tests\\WikiTextFixes).
"""

from __future__ import annotations

from src.main_app.services.new_html_services.domain.fixes.templates.delete_templates import (
    remove_lead_templates,
    remove_templates,
)

# ---------------------------------------------------------------------------
# Tests for remove_templates
# ---------------------------------------------------------------------------


class TestRemoveTemplates:
    """Tests for the `remove_templates` function of the `delete_templates` module."""

    def test_remove_templates_with_short_description(self):
        """The `Short description` template is removed while surrounding text remains."""
        text = "{{Short description|Test article}} Article content"
        result = remove_templates(text)

        assert "{{Short description|Test article}}" not in result
        assert "Article content" in result

    def test_remove_templates_with_multiple_delete_targets(self):
        """Several deletable templates are all removed."""
        text = "{{Featured article}} {{Good article}} Content {{Use dmy dates}}"
        result = remove_templates(text)

        assert "{{Featured article}}" not in result
        assert "{{Good article}}" not in result
        assert "{{Use dmy dates}}" not in result
        assert "Content" in result

    def test_remove_templates_with_stub_template(self):
        """A `*-stub` template is removed via the generic stub pattern."""
        text = "Article content {{Biology-stub}}"
        result = remove_templates(text)

        assert "{{Biology-stub}}" not in result
        assert "Article content" in result

    def test_remove_templates_with_pp_templates(self):
        """Page-protection templates (`pp-*`) are removed."""
        text = "{{pp-protected}} {{pp-semi}} Article content"
        result = remove_templates(text)

        assert "{{pp-protected}}" not in result
        assert "{{pp-semi}}" not in result

    def test_remove_templates_with_articles_pattern(self):
        """Templates matching the `Articles for/needing/...` pattern are removed."""
        text = "{{Articles for deletion}} {{Articles needing cleanup}} Content"
        result = remove_templates(text)

        assert "{{Articles for deletion}}" not in result
        assert "{{Articles needing cleanup}}" not in result

    def test_remove_templates_preserves_other_templates(self):
        """A non-deletable template (e.g. Infobox) is preserved."""
        text = "{{Short description|Test}} {{Infobox|param=value}} Content"
        result = remove_templates(text)

        assert "{{Short description|Test}}" not in result
        assert "{{Infobox|param=value}}" in result

    def test_remove_templates_with_case_insensitive(self):
        """Template name matching is case-insensitive."""
        text = "{{SHORT DESCRIPTION|Test}} {{Short Description|Test2}} Content"
        result = remove_templates(text)

        assert "SHORT DESCRIPTION" not in result
        assert "Short Description" not in result

    def test_remove_templates_with_unlinked_wikibase(self):
        """The `#unlinkedwikibase` parser-function-style template is removed."""
        text = "{{#unlinkedwikibase:test}} Content"
        result = remove_templates(text)

        assert "{{#unlinkedwikibase:test}}" not in result
        assert "Content" in result

    def test_remove_templates_with_use_spelling_templates(self):
        """`Use ... English/spelling` templates are removed."""
        text = "{{Use American English}} {{Use British spelling}} Content"
        result = remove_templates(text)

        assert "Use American English" not in result
        assert "Use British spelling" not in result

    def test_remove_templates_with_no_matching_templates(self):
        """Templates that don't match any deletion rule are preserved."""
        text = "{{Infobox|param=value}} {{Citation needed}} Content"
        result = remove_templates(text)

        # These templates should not be removed
        assert "{{Infobox|param=value}}" in result
        assert "{{Citation needed}}" in result

    def test_remove_templates_with_empty_text(self):
        """Empty input returns empty output."""
        result = remove_templates("")

        assert result == ""

    def test_remove_templates_with_no_templates(self):
        """Plain text with no templates at all is returned unchanged."""
        text = "Plain text without any templates"
        result = remove_templates(text)

        assert result == text

    def test_remove_templates_with_multiline_template(self):
        """A deletable template spanning multiple lines is removed as a whole."""
        text = "{{Short description\n|Test description\n}} Content"
        result = remove_templates(text)

        assert "Short description" not in result
        assert "Content" in result

    def test_remove_templates_with_nested_templates(self):
        """A deletable top-level template is removed while a nested short description
        inside a preserved Infobox is left alone."""
        text = "{{Use dmy dates}} {{Infobox|nested={{Short description|Test}}}} Content"
        result = remove_templates(text)

        assert "{{Use dmy dates}}" not in result
        # Infobox should be preserved even with nested short description
        assert "{{Infobox" in result

    def test_remove_templates_with_redirect_template(self):
        """The `Redirect` template is removed."""
        text = "{{Redirect|Test}} Article content"
        result = remove_templates(text)

        assert "{{Redirect|Test}}" not in result
        assert "Article content" in result

    def test_remove_templates_with_sprotect(self):
        """The `Sprotect` template is removed."""
        text = "{{Sprotect}} Content"
        result = remove_templates(text)

        assert "{{Sprotect}}" not in result

    def test_remove_templates_with_defaultsort(self):
        """`DEFAULTSORT:` is removed via the `defaultsort` prefix rule."""
        text = "Content {{DEFAULTSORT:Sort Key}}"
        result = remove_templates(text)

        assert "{{DEFAULTSORT:Sort Key}}" not in result
        assert "Content" in result

    def test_remove_templates_with_wikipedia_articles_pattern(self):
        """Templates matching the `Wikipedia articles ...` pattern are removed."""
        text = "{{Wikipedia articles needing cleanup}} Content"
        result = remove_templates(text)

        assert "Wikipedia articles needing cleanup" not in result


# ---------------------------------------------------------------------------
# Tests for remove_lead_templates
# ---------------------------------------------------------------------------


class TestRemoveLeadTemplates:
    """Tests for the `remove_lead_templates` function of the `delete_templates` module."""

    def test_remove_lead_templates_finds_infobox(self):
        """Content before an `{{Infobox ...}}` template is dropped."""
        text = "Pre-infobox content {{Infobox medical condition|name=Test}} Article content"
        result = remove_lead_templates(text)

        assert "Pre-infobox content" not in result
        assert result.startswith("{{Infobox medical condition")

    def test_remove_lead_templates_finds_drugbox(self):
        """Content before a `{{Drugbox ...}}` template is dropped."""
        text = "Header content {{Drugbox|name=Drug}} Main content"
        result = remove_lead_templates(text)

        assert "Header content" not in result
        assert result.startswith("{{Drugbox")

    def test_remove_lead_templates_finds_speciesbox(self):
        """Content before a `{{Speciesbox ...}}` template is dropped."""
        text = "Pre content {{Speciesbox|name=Species}} Article"
        result = remove_lead_templates(text)

        assert "Pre content" not in result
        assert result.startswith("{{Speciesbox")

    def test_remove_lead_templates_with_no_target_template(self):
        """Text with none of the recognized infobox-like templates is only stripped."""
        text = "Article content {{Other template}} more content"
        result = remove_lead_templates(text)

        # Should return text as is (trimmed)
        assert result == text.strip()

    def test_remove_lead_templates_case_insensitive(self):
        """The infobox prefix is matched case-insensitively."""
        text = "Header {{INFOBOX medical condition|param=value}} Content"
        result = remove_lead_templates(text)

        assert "Header" not in result
        assert "INFOBOX" in result

    def test_remove_lead_templates_with_empty_text(self):
        """Empty input returns empty output."""
        result = remove_lead_templates("")

        assert result == ""

    def test_remove_lead_templates_trims_result(self):
        """Leading/trailing whitespace around the retained infobox content is trimmed."""
        text = "   \n\n{{Infobox drug|name=Test}}   \n"
        result = remove_lead_templates(text)

        assert result.startswith("{{Infobox")
        assert result.strip() == result

    def test_remove_lead_templates_with_multiple_infoboxes(self):
        """When several matching templates are present, only content before the first is dropped."""
        text = "Pre {{Infobox 1}} and {{Drugbox}} content"
        result = remove_lead_templates(text)

        # Should find first matching template
        assert "Pre" not in result
        assert result.startswith("{{Infobox")
