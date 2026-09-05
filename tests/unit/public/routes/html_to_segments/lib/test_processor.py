"""
Unit tests for src/main_app/public/routes/html_to_segments/lib/processor.py module.

Functions to test: process_html
"""

from src.main_app.public.routes.html_to_segments.lib.processor import (
    process_html,
)


class TestProcessHtml:
    def test_process_html_with_simple_html(self):
        html = "<html><body><p>Simple paragraph.</p></body></html>"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><p id="2"><span class="cx-segment" data-segmentid="3">Simple paragraph.</span></p></section></body></html>'
        )

    def test_process_html_with_complex_html(self):
        html = "<html><body><h1>Title</h1><p>First paragraph.</p><p>Second paragraph.</p></body></html>"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><h1 id="2"><span class="cx-segment" data-segmentid="3">Title</span></h1></section><section data-mw-section-number="0" id="cxSourceSection1" rel="cx:Section"><p id="4"><span class="cx-segment" data-segmentid="5">First paragraph.</span></p><p id="6"><span class="cx-segment" data-segmentid="7">Second paragraph.</span></p></section></body></html>'
        )

    def test_process_html_with_empty_html(self):
        html = ""
        result = process_html(html)
        assert (
            result
            == '<body id="0"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><div id="1"></div></section></body>'
        )

    def test_process_html_returns_array(self):
        html = "<p>Test content</p>"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><p id="2"><span class="cx-segment" data-segmentid="3">Test content</span></p></section></body></html>'
        )

    def test_process_html_with_multiple_paragraphs(self):
        html = "<p>Paragraph 1</p><p>Paragraph 2</p><p>Paragraph 3</p>"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><p id="2"><span class="cx-segment" data-segmentid="3">Paragraph 1</span></p><p id="4"><span class="cx-segment" data-segmentid="5">Paragraph 2</span></p><p id="6"><span class="cx-segment" data-segmentid="7">Paragraph 3</span></p></section></body></html>'
        )

    def test_process_html_with_nested_elements(self):
        html = "<div><p>Text with <strong>bold</strong> and <em>italic</em>.</p></div>"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><div id="2"><p id="3"><span class="cx-segment" data-segmentid="4">Text with <strong>bold</strong> and <em>italic</em>.</span></p></div></section></body></html>'
        )

    def test_process_html_with_links(self):
        html = '<p>Text with <a href="#">link</a> inside.</p>'
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><p id="2"><span class="cx-segment" data-segmentid="3">Text with <a href="#">link</a> inside.</span></p></section></body></html>'
        )

    def test_process_html_with_lists(self):
        html = "<ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><ul id="2"><li id="3"><span class="cx-segment" data-segmentid="4">Item 1</span></li><li id="5"><span class="cx-segment" data-segmentid="6">Item 2</span></li><li id="7"><span class="cx-segment" data-segmentid="8">Item 3</span></li></ul></section></body></html>'
        )

    def test_process_html_with_headings(self):
        html = "<h2>Section 1</h2><p>Content</p><h2>Section 2</h2><p>More content</p>"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="1" id="cxSourceSection0" rel="cx:Section"><h2 id="2"><span class="cx-segment" data-segmentid="3">Section 1</span></h2></section><section data-mw-section-number="1" id="cxSourceSection1" rel="cx:Section"><p id="4"><span class="cx-segment" data-segmentid="5">Content</span></p></section><section data-mw-section-number="2" id="cxSourceSection2" rel="cx:Section"><h2 id="6"><span class="cx-segment" data-segmentid="7">Section 2</span></h2></section><section data-mw-section-number="2" id="cxSourceSection3" rel="cx:Section"><p id="8"><span class="cx-segment" data-segmentid="9">More content</span></p></section></body></html>'
        )

    def test_process_html_with_tables(self):
        html = "<table><tr><td>Cell 1</td><td>Cell 2</td></tr></table>"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><table id="2"><tr id="3"><td id="4"><span class="cx-segment" data-segmentid="5">Cell 1</span></td><td id="6"><span class="cx-segment" data-segmentid="7">Cell 2</span></td></tr></table></section></body></html>'
        )

    def test_process_html_with_special_characters(self):
        html = "<p>Text with special chars: &lt; &gt; &amp; &quot;</p>"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><p id="2"><span class="cx-segment" data-segmentid="3">Text with special chars: &#60; &#62; &#38; "</span></p></section></body></html>'
        )

    def test_process_html_handles_api_error(self):
        html = "<invalid>Malformed HTML"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><invalid>Malformed HTML</invalid></section></body></html>'
        )

    def test_process_html_with_large_html(self):
        paragraphs = "<p>This is a test paragraph with some content.</p>" * 50
        html = f"<html><body>{paragraphs}</body></html>"
        result = process_html(html)
        expected_segments = "".join(
            f'<p id="{i*2+2}"><span class="cx-segment" data-segmentid="{i*2+3}">This is a test paragraph with some content.</span></p>'
            for i in range(50)
        )
        assert (
            result
            == f'<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section">{expected_segments}</section></body></html>'
        )

    def test_process_html_with_references(self):
        html = '<p>Text with reference<sup><a href="#ref1">[1]</a></sup>.</p>'
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><p id="2"><span class="cx-segment" data-segmentid="3">Text with reference<sup><a href="#ref1">[1]</a></sup>.</span></p></section></body></html>'
        )

    def test_process_html_with_divs(self):
        html = '<div class="section"><p>Content in div</p></div>'
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><div class="section" id="2"><p id="3"><span class="cx-segment" data-segmentid="4">Content in div</span></p></div></section></body></html>'
        )

    def test_process_html_result_format(self):
        html = "<p>Test paragraph</p>"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><p id="2"><span class="cx-segment" data-segmentid="3">Test paragraph</span></p></section></body></html>'
        )

    def test_process_html_with_break_tags(self):
        html = "<p>Line 1<br>Line 2<br>Line 3</p>"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><p id="2"><span class="cx-segment" data-segmentid="3">Line 1<br />Line 2<br />Line 3</span></p></section></body></html>'
        )

    def test_process_html_with_images(self):
        html = '<p>Text with <img src="test.jpg" alt="Image"> image.</p>'
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><p id="2"><span class="cx-segment" data-segmentid="3">Text with <img alt="Image" src="test.jpg" /> image.</span></p></section></body></html>'
        )

    def test_process_html_with_inline_styles(self):
        html = '<p style="color: red;">Styled paragraph</p>'
        result = process_html(html)
        result1 = process_html(html, "ar")
        assert result == result1
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><p id="2" style="color: red;"><span class="cx-segment" data-segmentid="3">Styled paragraph</span></p></section></body></html>'
        )

    def test_process_html_with_unicode_characters(self):
        html = "<p>Text with unicode: ñ, é, ü, 中文, العربية</p>"
        result = process_html(html)
        assert (
            result
            == '<html id="0"><body id="1"><section data-mw-section-number="0" id="cxSourceSection0" rel="cx:Section"><p id="2"><span class="cx-segment" data-segmentid="3">Text with unicode: ñ, é, ü, 中文, العربية</span></p></section></body></html>'
        )
