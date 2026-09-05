"""
Unit tests for
src/main_app/services/new_html_services/domain/fixes/media/remove_missing_images.py

Ported from the PHP suite ``RemoveMissingImagesTest`` (FixRefs\\Tests\\Domain).

Notes on the port:
- The PHP service has a regex-based fallback (``removeMissingInfoboxImagesRegex``)
  that operates on bare ``|image=`` / ``|caption=`` lines that are not wrapped in
  a ``{{...}}`` template call. The Python port only walks templates found by
  ``wikitextparser`` (``parsed.templates``), so infobox-style fixtures below are
  wrapped in a template call (e.g. ``{{Infobox ...}}``) to exercise the
  equivalent code path.
- Inline ``[[File:...]]`` / ``[[Image:...]]`` removal uses wikitextparser's
  wikilink parsing rather than PHP's manual bracket counter, but the observable
  behavior (whole link removed, surrounding text preserved, nested links inside
  captions handled correctly) is the same, so those fixtures are ported with
  the exact same input/expected strings as the PHP originals.
- Infobox assertions use substring checks (rather than exact-string equality)
  since the precise whitespace produced by ``template_helpers.delete_parameter``
  is an implementation detail not being ported here; the exact-match PHP
  assertions are only kept for the inline-image tests where the removal logic
  is simple string splicing.
"""

from __future__ import annotations

import re
from unittest.mock import patch

import pytest

from src.main_app.services.new_html_services.domain.fixes.media.remove_missing_images import (
    ImageExistenceChecker,
    RemoveMissingImagesService,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def service() -> RemoveMissingImagesService:
    return RemoveMissingImagesService()


@pytest.fixture
def mock_image_exists():
    """Patch ImageExistenceChecker.image_exists for the duration of a test.

    Yields the ``MagicMock`` so tests can configure its behavior via
    ``setup_mock_image_exists`` (mirrors the PHP helper
    ``setupMockImageExists``).
    """
    with patch.object(ImageExistenceChecker, "image_exists", autospec=True) as mocked:
        yield mocked


def setup_mock_image_exists(mock, file_exists_map: dict[str, bool]) -> None:
    """Configure the mocked ``image_exists`` to look up a filename->bool map.

    Strips a leading ``File:``/``Image:`` prefix before lookup, same as the
    PHP test helper, and defaults to ``False`` for anything not in the map.
    """

    def side_effect(self, filename: str) -> bool:
        clean = re.sub(r"^(File|Image):", "", filename, flags=re.IGNORECASE).strip()
        return file_exists_map.get(clean, False)

    mock.side_effect = side_effect


# ---------------------------------------------------------------------------
# Infobox image tests
# ---------------------------------------------------------------------------


class TestRemoveInfoboxImages:
    def test_infobox_image_exists(self, service, mock_image_exists):
        """TEST 1: Infobox image exists - no changes."""
        setup_mock_image_exists(mock_image_exists, {"AwareLogo.png": True})

        input_text = (
            "{{Infobox disease\n"
            "|name ={{PAGENAME}}\n"
            "|image =AwareLogo.png\n"
            "|caption =This is a valid image\n"
            "|specialty =[[Orthopedics]]\n"
            "}}"
        )

        result = service.remove_missing_infobox_images(input_text)

        assert result == input_text

    def test_infobox_image_missing(self, service, mock_image_exists):
        """TEST 2: Infobox image missing - remove image and caption."""
        setup_mock_image_exists(mock_image_exists, {"Non_existent_image_xyz789.png": False})

        input_text = (
            "{{Infobox disease\n"
            "|name ={{PAGENAME}}\n"
            "|image =Non_existent_image_xyz789.png\n"
            "|caption =This caption should be removed\n"
            "|specialty =[[Orthopedics]]\n"
            "}}"
        )

        result = service.remove_missing_infobox_images(input_text)

        assert "Non_existent_image_xyz789.png" not in result
        assert "This caption should be removed" not in result
        assert "|specialty =[[Orthopedics]]" in result
        assert "{{PAGENAME}}" in result

    def test_infobox_empty_image(self, service, mock_image_exists):
        """TEST 3: Empty infobox image field - remove both image and caption."""
        setup_mock_image_exists(mock_image_exists, {})

        input_text = (
            "{{Infobox disease\n"
            "|name ={{PAGENAME}}\n"
            "|image =\n"
            "|caption =Caption for empty image\n"
            "|specialty =[[Orthopedics]]\n"
            "}}"
        )

        result = service.remove_missing_infobox_images(input_text)

        assert "Caption for empty image" not in result
        assert "|specialty =[[Orthopedics]]" in result

    def test_infobox_multiple_images_mixed(self, service, mock_image_exists):
        """TEST 4: Multiple infobox images - mixed existence."""
        setup_mock_image_exists(
            mock_image_exists,
            {
                "AwareLogo.png": True,
                "Missing_image_xyz123456.png": False,
            },
        )

        input_text = (
            "{{Infobox disease\n"
            "|name ={{PAGENAME}}\n"
            "|image =AwareLogo.png\n"
            "|caption =Valid caption\n"
            "|image2 =Missing_image_xyz123456.png\n"
            "|caption2 =This should be removed\n"
            "|specialty =[[Orthopedics]]\n"
            "}}"
        )

        result = service.remove_missing_infobox_images(input_text)

        assert "|image =AwareLogo.png" in result
        assert "|caption =Valid caption" in result
        assert "Missing_image_xyz123456.png" not in result
        assert "This should be removed" not in result
        assert "|specialty =[[Orthopedics]]" in result


# ---------------------------------------------------------------------------
# Inline image tests
# ---------------------------------------------------------------------------


class TestRemoveMissingInlineImages:
    def test_inline_image_exists(self, service, mock_image_exists):
        """TEST 5: Inline image exists - no changes."""
        setup_mock_image_exists(mock_image_exists, {"AwareLogo.png": True})

        input_text = (
            "This is some text with an image:\n[[File:AwareLogo.png|thumb|A valid image caption]]\nMore text here."
        )

        result = service.remove_missing_inline_images(input_text)

        assert result == input_text

    def test_inline_image_missing(self, service, mock_image_exists):
        """TEST 6: Inline image missing - remove entire block."""
        setup_mock_image_exists(mock_image_exists, {"Non_existent_image_xyz654.png": False})

        input_text = (
            "This is some text with an image:\n"
            "[[File:Non_existent_image_xyz654.png|thumb|This should be removed]]\n"
            "More text here."
        )
        expected = "This is some text with an image:\n\nMore text here."

        result = service.remove_missing_inline_images(input_text)

        assert result == expected

    def test_inline_multiple_images_mixed(self, service, mock_image_exists):
        """TEST 7: Multiple inline images - mixed existence."""
        setup_mock_image_exists(
            mock_image_exists,
            {
                "AwareLogo.png": True,
                "Missing_file_xyz987.jpg": False,
            },
        )

        input_text = (
            "Start of article.\n"
            "[[File:AwareLogo.png|thumb|Keep this image]]\n"
            "Some middle text.\n"
            "[[File:Missing_file_xyz987.jpg|left|200px|Remove this]]\n"
            "End of article."
        )
        expected = (
            "Start of article.\n[[File:AwareLogo.png|thumb|Keep this image]]\nSome middle text.\n\nEnd of article."
        )

        result = service.remove_missing_inline_images(input_text)

        assert result == expected

    def test_inline_image_nested_links(self, service, mock_image_exists):
        """TEST 8: Inline image with nested links in caption."""
        setup_mock_image_exists(mock_image_exists, {"Missing_image_nested_xyz321.png": False})

        input_text = "[[File:Missing_image_nested_xyz321.png|thumb|See [[Orthopedics]] for more info]]"
        expected = ""

        result = service.remove_missing_inline_images(input_text)

        assert result == expected

    def test_inline_image_prefix_missing(self, service, mock_image_exists):
        """TEST 9: Inline image using Image: prefix (alias) - missing."""
        setup_mock_image_exists(mock_image_exists, {"Non_existent_old_xyz111.png": False})

        input_text = "[[Image:Non_existent_old_xyz111.png|thumb|Old style image link]]"
        expected = ""

        result = service.remove_missing_inline_images(input_text)

        assert result == expected

    def test_inline_image_prefix_exists(self, service, mock_image_exists):
        """TEST 10: Inline image exists using Image: prefix."""
        setup_mock_image_exists(mock_image_exists, {"AwareLogo.png": True})

        input_text = "[[Image:AwareLogo.png|thumb|Old style but valid]]"

        result = service.remove_missing_inline_images(input_text)

        assert result == input_text


# ---------------------------------------------------------------------------
# Combined / edge case tests
# ---------------------------------------------------------------------------


class TestImages:

    def test_combined_mixed(self, service, mock_image_exists):
        """TEST 11: Both infobox and inline images - mixed."""
        setup_mock_image_exists(
            mock_image_exists,
            {
                "Non_existent_infobox_xyz222.png": False,
                "Gallstones.png": True,
                "Another_missing_xyz333.jpg": False,
            },
        )

        input_text = (
            "{{Infobox disease|name={{PAGENAME}}|image=Non_existent_infobox_xyz222.png"
            "|caption=Remove this caption|specialty=[[Orthopedics]]}}"
            "This article discusses the condition."
            "[[File:Gallstones.png|thumb|right|A valid inline image]]"
            "More information here."
            "[[File:Another_missing_xyz333.jpg|left|Remove this too]]"
            "End of article."
        )

        result = service.remove_missing_images(input_text)

        assert "[[File:Gallstones.png|thumb|right|A valid inline image]]" in result
        assert "Non_existent_infobox_xyz222.png" not in result
        assert "Remove this caption" not in result
        assert "Another_missing_xyz333.jpg" not in result
        assert "{{PAGENAME}}" in result
        assert "specialty=[[Orthopedics]]" in result

    def test_no_images(self, service, mock_image_exists):
        """TEST 12: No images at all - no changes."""
        setup_mock_image_exists(mock_image_exists, {})

        input_text = (
            "|name ={{PAGENAME}}\n"
            "|synonym =\n"
            "|specialty =[[Orthopedics]]\n\n"
            "This is just plain text without any images."
        )

        result = service.remove_missing_images(input_text)

        assert result == input_text

    def test_complex_nested_caption_not_on_commons(self, service, mock_image_exists):
        """TEST 13: Complex nested caption with a missing image is fully removed."""
        setup_mock_image_exists(mock_image_exists, {"AwareLogo.png": False})

        input_text = "[[File:AwareLogo.png|thumb|upright=1.3|Logo of the [[WHO]] Aware [[Classification]]]]__NOTOC__"

        result = service.remove_missing_inline_images(input_text)

        assert result == "__NOTOC__"

    def test_complex_nested_caption_on_commons(self, service, mock_image_exists):
        """TEST 14: Complex nested caption with an existing image is left untouched."""
        setup_mock_image_exists(mock_image_exists, {"Gallstones.png": True})

        input_text = (
            "[[File:Gallstones.png|thumb|upright=1.3|"
            "Gallstones typically form in the [[gallbladder]] and may result in symptoms if they block the biliary system.]]"
        )

        result = service.remove_missing_inline_images(input_text)

        assert result == input_text


# ---------------------------------------------------------------------------
# ImageExistenceChecker tests (bonus coverage for the Python-only helper
# class, which the PHP suite mocked out entirely via
# CommonsImageServiceInterface)
# ---------------------------------------------------------------------------


class _FakeHttpClient:
    """Minimal stand-in for HttpClientService used by ImageExistenceChecker."""

    def __init__(self, response_array):
        self._response_array = response_array
        self.last_params = None

    def request(self, url: str, method, params):
        self.last_params = params
        return self._response_array


def _make_checker(response_array) -> ImageExistenceChecker:
    checker = ImageExistenceChecker()
    checker.http_client = _FakeHttpClient(response_array)  # pyright: ignore[reportAttributeAccessIssue]
    return checker


class TestImageExists:
    def test_image_exists_true_when_page_present(self):
        response = {"output": ('{"query": {"pages": {"12345": {"pageid": 12345, "title": "File:AwareLogo.png"}}}}')}
        checker = _make_checker(response)

        assert checker.image_exists("AwareLogo.png") is True

    def test_image_exists_false_when_page_missing_key(self):
        response = {"output": ('{"query": {"pages": {"-1": {"missing": "", "title": "File:Nope.png"}}}}')}
        checker = _make_checker(response)

        assert checker.image_exists("File:Nope.png") is False

    def test_image_exists_strips_file_and_image_prefix(self):
        response = {"output": ('{"query": {"pages": {"1": {"pageid": 1, "title": "File:Foo.png"}}}}')}
        checker = _make_checker(response)

        assert checker.image_exists("Image:Foo.png") is True

    def test_image_exists_empty_filename_returns_false(self):
        checker = _make_checker({"output": "{}"})

        assert checker.image_exists("") is False
        assert checker.image_exists("   ") is False

    def test_image_exists_defaults_to_true_on_http_error(self):
        checker = _make_checker({"error_code": 500, "error": "boom"})

        assert checker.image_exists("Whatever.png") is True

    def test_image_exists_defaults_to_true_on_bad_json(self):
        checker = _make_checker({"output": "not json"})

        assert checker.image_exists("Whatever.png") is True
