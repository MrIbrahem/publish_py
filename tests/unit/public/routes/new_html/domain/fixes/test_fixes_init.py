"""
Unit tests for src/main_app/public/routes/new_html/domain/fixes/__init__.py module.

Classes to test: WikitextFixerService
"""


import os
from pathlib import Path

from src.main_app.public.routes.new_html.domain.fixes import (
    WikitextFixerService,
)

def strip_result(result: str) -> str:
    text = result.strip()
    # remove empty space from end of each line of text
    text = "\n".join([line.rstrip() for line in text.splitlines()])
    return text


class TestWikitextFixerService:
    def load_fixture(self, name: str) -> str:
        path = Path(__file__).parent / "data" / name
        assert path.exists(), f"Fixture file missing: {path}"

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert content is not None, f"Unable to read fixture file: {path}"
        return content

    def test_fix_wikitext_matches_result_fixture(self):
        source = self.load_fixture('source-1.wiki')
        expected = self.load_fixture('result-1.wiki')

        fixer = WikitextFixerService()
        result = fixer.fix(text=source, title="PLACEHOLDER_TEST")
        if result.strip() != expected.strip():
            # write to output-1.wiki
            output_path = Path(__file__).parent / "data" / "output-1.wiki"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)

        assert strip_result(result) == strip_result(expected)
