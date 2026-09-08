"""
Unit tests for src/main_app/services/new_html_services/wikitext_fixes/__init__.py module.

Classes to test: WikitextFixerService
"""

from pathlib import Path

import pytest

from src.main_app.services.new_html_services.wikitext_fixes import (
    WikitextFixerService,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures"

all_flags = {
    "abdominal_pain.wiki": False,
}
# fixture_files = [("test-1.wiki"), ("test-2.wiki")]
FIXTURE_FILES = [(x.name, all_flags.get(x.name, True)) for x in (FIXTURE_PATH / "source").glob("*.wiki")]


def strip_result(result: str) -> str:
    text = result.strip()
    # remove empty space from end of each line of text
    text = "\n".join([line.rstrip() for line in text.splitlines()])
    return text.strip()


class TestWikitextFixerService:
    def load_fixture(self, name: str, folder: str = "source") -> str:
        path = FIXTURE_PATH / folder / name
        assert path.exists(), f"Fixture file missing: {path}"

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        assert content is not None, f"Unable to read fixture file: {path}"
        return content

    @pytest.mark.parametrize("file, all_flag", FIXTURE_FILES)
    def test_fix_wikitext_matches_result_fixture(self, file: str, all_flag: bool) -> None:
        source = self.load_fixture(file, "source")
        expected = self.load_fixture(file, "result")
        expected = strip_result(expected)

        fixer = WikitextFixerService()
        result = fixer.fix(text=source, title="PLACEHOLDER_TEST", all_flag=all_flag)
        result = strip_result(result)

        if result != expected:
            # write to output-1.wiki
            output_path = FIXTURE_PATH / "output" / file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result + "\n")

        assert result == expected
