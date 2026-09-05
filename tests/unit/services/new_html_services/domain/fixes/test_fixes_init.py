"""
Unit tests for src/main_app/services/new_html_services/domain/fixes/__init__.py module.

Classes to test: WikitextFixerService
"""

import os

from src.main_app.services.new_html_services.domain.fixes import (
    WikitextFixerService,
)


class TestWikitextFixerService:
    def load_fixture(self, name: str) -> str:
        path = os.path.join(os.path.dirname(__file__), "data", name)
        assert os.path.exists(path), f"Fixture file missing: {path}"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert content is not None, f"Unable to read fixture file: {path}"
        return content

    def test_fix_wikitext_matches_result_fixture(self):
        source = self.load_fixture("source-1.wiki")
        expected = self.load_fixture("result-1.wiki")

        fixer = WikitextFixerService()
        result = fixer.fix(text=source, title="PLACEHOLDER_TEST")

        assert result.strip() == expected.strip()

    def test_fix_wikitext_is_deterministic(self):
        source = self.load_fixture("source-1.wiki")

        fixer = WikitextFixerService()
        first = fixer.fix(text=source, title="PLACEHOLDER_TEST")
        second = fixer.fix(text=source, title="PLACEHOLDER_TEST")

        assert first == second

    def test_fix_wikitext_with_empty_input_returns_empty(self):
        fixer = WikitextFixerService()
        result = fixer.fix(text="", title="PLACEHOLDER_TEST")
        assert result == ""
