"""
Unit tests for HTML post-processing utility functions.

Imports the functions under test from src.main_app.public.routes.new_html.services.html_utils.
"""

from src.main_app.public.routes.new_html.services.html_utils import (
    del_div_error,
    fix_link_red,
    remove_data_parsoid,
)


class TestDelDivError:
    """
    Tests for del_div_error function
    """

    def test_removes_single_error_div(self):
        html = '<div>Normal content</div><div class="error">Error message</div><div>More content</div>'
        result = del_div_error(html)
        assert "Error message" not in result
        assert "Normal content" in result
        assert "More content" in result

    def test_removes_multiple_error_divs(self):
        html = '<div class="error">Error 1</div><div>Content</div><div class="error">Error 2</div>'
        result = del_div_error(html)

        assert "Error 1" not in result
        assert "Error 2" not in result
        assert "Content" in result

    def test_preserves_non_error_divs(self):
        html = '<div class="info">Info</div><div class="error">Error</div><div class="warning">Warning</div>'
        result = del_div_error(html)

        assert "Info" in result
        assert "Warning" in result
        assert "Error" not in result

    def test_with_no_error_divs(self):
        html = "<div>Content 1</div><div>Content 2</div>"
        result = del_div_error(html)

        assert result == html

    def test_with_empty_html(self):
        result = del_div_error("")
        assert result == ""

    def test_with_single_quotes(self):
        html = "<div class='error'>Error message</div>"
        result = del_div_error(html)

        assert "Error message" not in result

    def test_with_nested_content(self):
        html = '<div class="error">Error with <span>nested</span> content</div>'
        result = del_div_error(html)

        assert "Error with" not in result
        assert "nested" not in result

    def test_with_multiline_div(self):
        html = '<div class="error">\nMultiline\nerror\nmessage\n</div>'
        result = del_div_error(html)

        assert "Multiline" not in result
        assert "error" not in result

    def test_with_adjacent_divs(self):
        html = '<div>Before</div><div class="error">Error</div><div>After</div>'
        result = del_div_error(html)

        assert "<div>Before</div>" in result
        assert "<div>After</div>" in result
        assert "Error" not in result

class TestFixLinkRed:
    """
    tests for fix_link_red method
    """

    def test_removes_edit_links(self):
        html = (
            '<a rel="mw:ExtLink" href="//en.wikipedia.org/w/index.php?title=Video:Test&veaction=edit" '
            'class="external text"><span class="mw-ui-button mw-ui-progressive">Edit with VisualEditor</span></a> test!'
        )
        result = fix_link_red(html)

        assert "Edit with VisualEditor" not in result
        assert result == " test!"

    def test_fixes_red_links(self):
        html = '<a typeof="mw:LocalizedAttrs" href="/wiki/Test?action=edit&redlink=1">Red Link</a>'
        result = fix_link_red(html)

        assert "action=edit" not in result
        assert "redlink=1" not in result
        assert result == '<a href="/wiki/Test">Red Link</a>'

    def test_preserves_normal_links(self):
        html = '<a href="/wiki/Article">Normal Link</a>'
        result = fix_link_red(html)

        assert "Normal Link" in result
        assert 'href="/wiki/Article"' in result
        assert result == '<a href="/wiki/Article">Normal Link</a>'

    def test_with_no_links(self):
        html = "<p>Content without links</p>"
        result = fix_link_red(html)

        assert result == html

    def test_with_empty_html(self):
        result = fix_link_red("")
        assert result == ""

    def test_with_multiple_red_links(self):
        html = (
            '<a typeof="mw:LocalizedAttrs" href="/test?action=edit&redlink=1">Red1</a> '
            '<a typeof="mw:LocalizedAttrs" href="/test2?action=edit&redlink=1">Red2</a>'
        )
        result = fix_link_red(html)

        assert "action=edit" not in result
        assert "redlink=1" not in result
        assert result == '<a href="/test">Red1</a> <a href="/test2">Red2</a>'

    def test_removes_typeof_attribute(self):
        html = '<a typeof="mw:LocalizedAttrs" href="/wiki/Test?action=edit">Link</a>'
        result = fix_link_red(html)

        # Should remove typeof and other attributes when processing red links
        assert isinstance(result, str)
        assert result == '<a href="/wiki/Test">Link</a>'


class TestRemoveDataParsoid:
    """
    tests for remove_data_parsoid method
    """

    def test_with_localized_attrs_but_no_action_edit(self):
        """
        Covers the branch where 'mw:LocalizedAttrs' is present in options
        but href does NOT contain 'action=edit' (the `if` body at line 70
        is skipped, so href/attrs_to_del are left untouched).
        """
        html = '<a typeof="mw:LocalizedAttrs" href="/wiki/NormalPage">Link</a>'
        result = fix_link_red(html)

        assert 'typeof="mw:LocalizedAttrs"' in result
        # attrs_to_del (typeof, data-mw-i18n, class) are NOT removed
        # since the "action=edit" branch never executes

        assert result in (
            '<a typeof="mw:LocalizedAttrs" href="/wiki/NormalPage">Link</a>',
            '<a href="/wiki/NormalPage" typeof="mw:LocalizedAttrs">Link</a>',
        )

    def test_removes_attribute(self):
        html = '<a href="/wiki/Article" data-parsoid="{}">Link</a>'
        result = remove_data_parsoid(html)

        assert "data-parsoid" not in result
        assert 'href="/wiki/Article"' in result
        assert "Link" in result
        assert result == '<a href="/wiki/Article">Link</a>'

    def test_with_complex_data(self):
        html = '<a href="/wiki/Article" data-parsoid=\'{"dsr":[0,10,2,2]}\'>Link</a>'
        result = remove_data_parsoid(html)

        assert "data-parsoid" not in result
        assert "Link" in result
        assert result == '<a href="/wiki/Article">Link</a>'

    def test_with_multiple_links(self):
        html = '<a data-parsoid="{}">Link1</a> <a data-parsoid="{}">Link2</a>'
        result = remove_data_parsoid(html)

        assert "data-parsoid" not in result
        assert "Link1" in result
        assert "Link2" in result
        assert result == "<a>Link1</a> <a>Link2</a>"

    def test_preserves_other_attributes(self):
        html = '<a href="/wiki/Article" class="link" data-parsoid="{}">Link</a>'
        result = remove_data_parsoid(html)

        assert 'href="/wiki/Article"' in result
        assert 'class="link"' in result
        assert "data-parsoid" not in result
        assert result == '<a class="link" href="/wiki/Article">Link</a>'

    def test_with_no_data_parsoid(self):
        html = '<a href="/wiki/Article">Normal Link</a>'
        result = remove_data_parsoid(html)

        assert result == html

    def test_with_regex_patterns(self):
        html = '<div data-parsoid="{}">Content</div><span data-parsoid=\'{"test":"value"}\'>More</span>'
        result = remove_data_parsoid(html)

        assert result == "<div>Content</div><span>More</span>"
        assert "data-parsoid" not in result
        assert "Content" in result
        assert "More" in result

    def test_with_nested_links(self):
        html = '<div><a data-parsoid="{}">Link 1</a> and <a data-parsoid="{}">Link 2</a></div>'
        result = remove_data_parsoid(html)

        assert "data-parsoid" not in result
        assert "Link 1" in result
        assert "Link 2" in result
        assert result == "<div><a>Link 1</a> and <a>Link 2</a></div>"

    def test_removes_data_parsoid_attribute(self):
        html = '<a href="/wiki/Article" data-parsoid="{}">Link</a>'
        result = remove_data_parsoid(html)

        assert result == '<a href="/wiki/Article">Link</a>'
        assert "data-parsoid" not in result

    def test_preserves_link_without_data_parsoid(self):
        html = '<a href="/wiki/Article">Normal Link</a>'
        result = remove_data_parsoid(html)

        assert result == html

    def test_removes_data_parsoid_with_single_quotes_and_complex_value(self):
        html = '<a data-parsoid=\'{"dsr":[0,10,2,2]}\' href="/wiki/Article">Link</a>'
        result = remove_data_parsoid(html)

        assert "data-parsoid" not in result
        assert 'href="/wiki/Article"' in result
        assert "Link" in result
        assert result == '<a href="/wiki/Article">Link</a>'

    def test_with_only_data_parsoid_attribute(self):
        html = '<a data-parsoid="{}">OnlyDataParsoid</a>'
        result = remove_data_parsoid(html)

        assert result == "<a>OnlyDataParsoid</a>"
        assert "data-parsoid" not in result

    def test_with_multiple_links_only_one_has_data_parsoid(self):
        html = '<a href="/a" data-parsoid="{}">Link1</a> <a href="/b">Link2</a>'
        result = remove_data_parsoid(html)

        assert result == '<a href="/a">Link1</a> <a href="/b">Link2</a>'

    def test_with_multiple_links_both_have_data_parsoid(self):
        html = '<a href="/a" data-parsoid="{}">Link1</a> <a href="/b" data-parsoid="{}">Link2</a>'
        result = remove_data_parsoid(html)

        assert result == '<a href="/a">Link1</a> <a href="/b">Link2</a>'
        assert "data-parsoid" not in result

    def test_with_empty_html(self):
        result = remove_data_parsoid("")
        assert result == ""

    def test_with_no_anchor_tags(self):
        html = "<p>no links here</p>"
        result = remove_data_parsoid(html)

        assert result == html

    def test_preserves_other_attributes_and_their_order(self):
        html = '<a class="link" data-parsoid="{}" id="main">Content</a>'
        result = remove_data_parsoid(html)

        assert result == '<a class="link" id="main">Content</a>'
        assert "data-parsoid" not in result

    def test_with_nested_content_inside_link(self):
        html = '<a data-parsoid="{}">Text with <span>nested</span> content</a>'
        result = remove_data_parsoid(html)

        assert result == "<a>Text with <span>nested</span> content</a>"
        assert "data-parsoid" not in result

    def test_is_case_insensitive_for_data_parsoid_detection(self):
        html = '<a href="/wiki/Article" DATA-PARSOID="{}">Link</a>'
        result = remove_data_parsoid(html)

        assert result == '<a href="/wiki/Article">Link</a>'
        assert "data-parsoid" not in result.lower()
