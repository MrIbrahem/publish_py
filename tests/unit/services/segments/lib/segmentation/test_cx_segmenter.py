# ruff: noqa: F401
"""
Unit tests for src/main_app/services/segments/lib/segmentation/cx_segmenter.py module.

Classes to test: CXSegmenter

TODO: write tests
"""

from src.main_app.services.segments.lib.lineardoc import Doc, MwContextualizer, Parser
from src.main_app.services.segments.lib.mw.mw_page_loader import MWPageLoader
from src.main_app.services.segments.lib.segmentation.cx_segmenter import (
    CXSegmenter,
)
from tests.unit.html_normalizer import normalize_test_base


def get_parsed_doc(content, config=None, options=None) -> Doc:
    parser = Parser(MwContextualizer(config=config), options=options)
    parser.init()
    parser.write(content)
    return parser.builder.doc


def test_cx_segmenter_1():

    source_text = "<p>Some in the UK. Others in the US.</p>"

    expected_text = """
        <p id="0">
            <span class="cx-segment" data-segmentid="1">Some in the UK. </span>
            <span class="cx-segment" data-segmentid="2">Others in the US.</span>
        </p>
    """
    sort_attrs = True
    doc = MWPageLoader().get_page(
        source_html=source_text,
        lang="en",
        sort_attrs=sort_attrs,
        wrap_sections=False,
    )
    result = doc.get_html()

    normalized_result = normalize_test_base(result, sort_attrs=sort_attrs)

    expected_result_data = normalize_test_base(expected_text, sort_attrs=sort_attrs)

    assert normalized_result == expected_result_data
