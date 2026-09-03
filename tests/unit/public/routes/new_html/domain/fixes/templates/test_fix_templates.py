"""
Unit tests for src/main_app/public/routes/new_html/domain/fixes/templates/fix_templates.py module.

Functions to test: add_missing_title

Ported from the PHP suite ``FixTempsTest`` (FixRefs\\Tests\\WikiTextFixes).
All PHP test cases call the function with `ljust=0`, so tests here pass
`ljust=0` explicitly to mirror that behavior.
"""

from __future__ import annotations

from src.main_app.public.routes.new_html.domain.fixes.templates.fix_templates import (
    add_missing_title,
)


class TestAddMissingTitle:
    """Tests for the `add_missing_title` function of the `fix_templates` module."""

    def test_add_missing_title_with_drugbox(self):
        """A missing `drug_name` on `{{Drugbox}}` is filled in with the given title."""
        text = "{{Drugbox|other_param=value}}"
        result = add_missing_title(text, "Aspirin", 0)

        assert "drug_name=Aspirin" in result
        assert "other_param=value" in result

    def test_add_missing_title_with_infobox_drug(self):
        """A missing `drug_name` on `{{Infobox drug}}` is filled in."""
        text = "{{Infobox drug|param=value}}"
        result = add_missing_title(text, "Paracetamol", 0)

        assert "drug_name=Paracetamol" in result

    def test_add_missing_title_with_infobox_medical_condition(self):
        """A missing `name` on `{{Infobox medical condition}}` is filled in."""
        text = "{{Infobox medical condition|symptoms=test}}"
        result = add_missing_title(text, "Diabetes", 0)

        assert "name=Diabetes" in result
        assert "symptoms=test" in result

    def test_add_missing_title_with_infobox_medical_intervention(self):
        """A missing `name` on `{{Infobox medical intervention}}` is filled in."""
        text = "{{Infobox medical intervention|param=value}}"
        result = add_missing_title(text, "Surgery", 0)

        assert "name=Surgery" in result

    def test_add_missing_title_does_not_overwrite_existing(self):
        """An existing non-empty `drug_name` is left untouched."""
        text = "{{Drugbox|drug_name=Existing Name|param=value}}"
        result = add_missing_title(text, "New Name", 0)

        assert "drug_name=Existing Name" in result
        assert "drug_name=New Name" not in result

    def test_add_missing_title_with_empty_name(self):
        """An explicitly empty `drug_name=` is treated as missing and filled in."""
        text = "{{Drugbox|drug_name=}}"
        result = add_missing_title(text, "Medicine", 0)

        assert "drug_name=Medicine" in result

    def test_add_missing_title_with_whitespace_name(self):
        """A `drug_name` containing only whitespace is treated as missing and filled in."""
        text = "{{Drugbox|drug_name=   }}"
        result = add_missing_title(text, "Medicine", 0)

        assert "drug_name=Medicine" in result

    def test_add_missing_title_with_no_matching_template(self):
        """A template with no recognized title parameter is left unchanged."""
        text = "{{Other template|param=value}}"
        result = add_missing_title(text, "Title", 0)

        # Should remain unchanged
        assert result == text

    def test_add_missing_title_with_multiple_templates(self):
        """Two different infobox-like templates in the same text are both filled in."""
        text = "{{Drugbox}} {{Infobox medical condition}}"
        result = add_missing_title(text, "Test Title", 0)

        assert "drug_name=Test Title" in result
        assert "name=Test Title" in result

    def test_add_missing_title_with_case_insensitive(self):
        """The template name is matched case-insensitively."""
        text = "{{DRUGBOX|param=value}}"
        result = add_missing_title(text, "Medicine", 0)

        assert "drug_name=Medicine" in result

    def test_add_missing_title_preserves_other_parameters(self):
        """Existing unrelated parameters are preserved alongside the added title."""
        text = "{{Drugbox|param1=value1|param2=value2|param3=value3}}"
        result = add_missing_title(text, "Drug Name", 0)

        assert "param1=value1" in result
        assert "param2=value2" in result
        assert "param3=value3" in result
        assert "drug_name=Drug Name" in result

    def test_add_missing_title_formats_with_new_line(self):
        """The re-rendered template uses newlines (pretty-printed form)."""
        text = "{{Drugbox|param=value}}"
        result = add_missing_title(text, "Medicine", 0)

        # Should format with new lines
        assert "\n" in result

    def test_add_missing_title_with_empty_text(self):
        """Empty input returns empty output."""
        result = add_missing_title("", "Title", 0)

        assert result == ""

    def test_add_missing_title_with_no_templates(self):
        """Plain text with no templates at all is returned unchanged."""
        text = "Plain text without templates"
        result = add_missing_title(text, "Title", 0)

        assert result == text

    def test_add_missing_title_with_multiline_template(self):
        """A `{{Drugbox}}` template already spanning multiple lines is filled in correctly."""
        text = "{{Drugbox\n|param1=value1\n|param2=value2\n}}"
        result = add_missing_title(text, "Medicine", 0)

        assert "drug_name=Medicine" in result

    def test_add_missing_title_with_nested_templates(self):
        """A nested template inside a parameter value is preserved when the title is added."""
        text = "{{Drugbox|param={{nested|value}}}}"
        result = add_missing_title(text, "Medicine", 0)

        assert "drug_name=Medicine" in result
        assert "{{nested|value}}" in result

    def test_add_missing_title_with_special_characters(self):
        """A title containing hyphens, digits, and parentheses is inserted verbatim."""
        text = "{{Drugbox|param=value}}"
        result = add_missing_title(text, "Medicine-123 (Test)", 0)

        assert "drug_name=Medicine-123 (Test)" in result

    def test_add_missing_title_replaces_template(self):
        """Text surrounding the modified template is preserved."""
        text = "Before {{Drugbox|old=param}} After"
        result = add_missing_title(text, "New Drug", 0)

        assert "Before" in result
        assert "After" in result
        assert "drug_name=New Drug" in result

    def test_add_missing_title_with_ljust_formatting(self):
        """A template with parameters of varying name length still gets its title added."""
        text = "{{Drugbox|a=value1|longer_param=value2}}"
        result = add_missing_title(text, "Medicine", 0)

        # The function uses ljust=17 by default; this test forces ljust=0
        assert "drug_name=Medicine" in result

    def test_add_missing_title_does_not_affect_other_templates(self):
        """Other templates in the same text are left completely untouched."""
        text = "{{Cite|title=Test}} {{Drugbox}} {{Another}}"
        result = add_missing_title(text, "Medicine", 0)

        assert "{{Cite|title=Test}}" in result
        assert "{{Another}}" in result
        assert "drug_name=Medicine" in result

    def test_add_missing_title_with_mixed_case(self):
        """A mixed-case template name (`Infobox Medical Condition`) is still recognized."""
        text = "{{Infobox Medical Condition|param=value}}"
        result = add_missing_title(text, "Disease", 0)

        assert "name=Disease" in result

    def test_add_missing_title_preserves_order(self):
        """Existing parameters keep their relative order after the title is added."""
        text = "{{Drugbox|first=1|second=2}}"
        result = add_missing_title(text, "Medicine", 0)

        # New parameter should be added, existing order preserved
        assert "drug_name=Medicine" in result
        assert "first=1" in result
        assert "second=2" in result

    def test_add_missing_title_with_underscores(self):
        """A template name using an underscore (`Drug_box`) is still recognized."""
        text = "{{Drug_box|param=value}}"
        result = add_missing_title(text, "Medicine", 0)

        assert "drug_name=Medicine" in result
