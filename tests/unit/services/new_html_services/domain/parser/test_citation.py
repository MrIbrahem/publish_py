"""
Unit tests for src/main_app/services/new_html_services/domain/parser/citation.py module.
"""

from src.main_app.services.new_html_services.domain.parser.citation import Citation

import wikitextparser as wtp

class TestCitation:

    def test_basic(self):
        text = "<ref name = PI2022></ref>"
        result = Citation.from_text(text)
        assert result.name == "PI2022"
        assert result.is_self_closing() is True

    def test_no_quetes_2(self):
        text = "<ref name = PI2022/>"
        wtp_tag = wtp._tag.Tag(text)
        result = Citation.from_text(text)

        assert result.is_self_closing() is True
        assert result.name == "PI2022"

