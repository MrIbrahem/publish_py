"""
Unit tests for src/main_app/services/new_html_services/domain/parser/citation.py module.
"""

import wikitextparser as wtp

from src.main_app.services.new_html_services.domain.parser.citation import Citation


class TestCitation:

    def test_basic(self):
        text = "<ref name = PI2022></ref>"
        result = Citation.from_text(text)
        assert result.name == "PI2022"
        assert result.is_self_closing() is True

    def test_for_bug(self):
        wtp_tag = wtp._tag.Tag("<ref name = PI2022/>")
        # BUG: Citation.from_text("<ref name = PI2022/>").name == "PI2022/" this should be fixed in Citation to become "PI2022"
        assert wtp_tag.attrs["name"] == "PI2022/"

        wtp_tag = wtp._tag.Tag("<ref name=PI2022/>")
        # this should be fixed in Citation to become "PI2022"
        assert wtp_tag.attrs["name"] == "PI2022/"

    def test_bug_fix(self):

        text = "<ref name = PI2022/>"
        result = Citation.from_text(text)
        new_text = Citation.fix_tag_name(text)

        assert new_text == "<ref name = PI2022 />"
        assert result.is_self_closing() is True
        assert result.name == "PI2022"

    def test_fix_tag_name(self):
        new_text = Citation.fix_tag_name("<ref name = PI2022/>")
        assert new_text == "<ref name = PI2022 />"

        new_text2 = Citation.fix_tag_name("<ref name = test/ >")
        assert new_text2 == "<ref name = test />"
