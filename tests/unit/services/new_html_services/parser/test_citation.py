"""
Unit tests for src/main_app/services/new_html_services/parser/citation.py module.
"""

import wikitextparser as wtp

from src.main_app.services.new_html_services.parser.citation import Citation


class TestCitation:

    def test_basic(self):
        text = "<ref name = PI2022></ref>"
        result = Citation.from_text(text)
        assert result.name == "PI2022"
        assert result.is_self_closing() is True

    def test_for_bug(self):
        """
        BUG: Citation.from_text("<ref name = PI2022/>").name == "PI2022/" this should be fixed in Citation to become "PI2022"
        This bug already solved in wikitextparser>0.55
        """
        wtp_tag = wtp._tag.Tag("<ref name = PI2022/>")
        # assert wtp_tag.attrs["name"] == "PI2022/"
        assert wtp_tag.attrs["name"] == "PI2022"

        wtp_tag = wtp._tag.Tag("<ref name=PI2022/>")
        # this should be fixed in Citation to become "PI2022"
        # assert wtp_tag.attrs["name"] == "PI2022/"
        assert wtp_tag.attrs["name"] == "PI2022"
