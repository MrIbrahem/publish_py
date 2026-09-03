"""
Missing image removal service.

Port of ``src/Domain/Fixes/Media/RemoveMissingImagesService.php``.

Template parameter handling uses ``domain.parser.template_helpers`` (built
on ``wikitextparser``). Inline ``[[File:...]]``/``[[Image:...]]`` removal
uses ``wikitextparser``'s wikilink parsing instead of the PHP version's
manual bracket-depth counter, since the parser already resolves nested
``[[...]]`` links inside captions correctly.
"""

from __future__ import annotations

import json
import re

import wikitextparser as wtp
from domain.parser import template_helpers as th
from ....services.clients import HttpClientService

_IMAGE_PARAM_RE = re.compile(r"^image(\d*)$", re.IGNORECASE)


class ImageExistenceChecker:
    """Equivalent of the PHP ``ImageExistenceChecker`` service to check image existence via MediaWiki API."""

    def __init__(self):
        """Initialize the checker with an HTTP client instance."""
        self.http_client = HttpClientService()

    def image_exists(self, filename: str) -> bool:
        """Check if an image exists on Wikimedia Commons.

        :param filename: The filename to check (with or without File:/Image: prefix).
        :return: True if the image exists or if API fails; False otherwise.
        """
        # Handle empty or whitespace-only filenames
        if not filename or not filename.strip():
            return False

        # Remove File: or Image: prefix case-insensitively
        filename = re.sub(r"^(File|Image):", "", filename, flags=re.IGNORECASE)
        filename = filename.strip()

        if not filename:
            return False

        params = {
            "action": "query",
            "titles": f"File:{filename}",
            "format": "json",
        }

        url = "https://commons.wikimedia.org/w/api.php"

        response_array = self.http_client.request(url, "GET", params)

        # Handle API or request errors (fallback to assuming the image exists)
        if response_array.get("error_code") or response_array.get("error"):
            return True

        response = response_array.get("output", "")
        if response == "" or response is None:
            return True

        try:
            data = json.loads(response) if isinstance(response, str) else response
            pages = data.get("query", {}).get("pages", {})

            # pages is typically a dict indexed by page IDs
            for _page_id, page in pages.items():
                return "missing" not in page

        except (json.JSONDecodeError, TypeError, AttributeError):
            # Assume exists on response parsing failure
            return True

        return False

class RemoveMissingImagesService:
    """Removes image references that don't exist on Commons from wikitext."""

    def __init__(self):
        """
        :param image_service: Service used to check whether an image file exists.
        """
        self._image_service = ImageExistenceChecker()

    def remove_missing_infobox_images(self, text: str) -> str:
        """Remove infobox images that don't exist on Commons.

        :param text: The wikitext to process.
        :return: The processed wikitext.
        """
        if not text:
            return text

        parsed = wtp.parse(text)

        for template in parsed.templates:
            # Snapshot parameter names first: deleting an argument while
            # iterating `template.arguments` would skip entries.
            param_names = [arg.name.strip() for arg in template.arguments]

            for param_name in param_names:
                match = _IMAGE_PARAM_RE.match(param_name)
                if not match:
                    continue

                image_number = match.group(1)  # "" for "image", "2" for "image2", ...
                filename = th.get_parameter(template, param_name).strip()

                if filename and self._image_service.image_exists(filename):
                    continue

                # Missing or empty: drop the image param and its caption.
                th.delete_parameter(template, param_name)

                caption_param = f"caption{image_number}"
                if th.has_parameter(template, caption_param):
                    th.delete_parameter(template, caption_param)

        text = str(parsed)
        text = self._remove_missing_infobox_images_regex(text)
        return text

    def _remove_missing_infobox_images_regex(self, text: str) -> str:
        """Remove missing infobox images given as raw ``|image=`` lines (fallback).

        Handles infobox-style fields that aren't wrapped in a ``{{...}}``
        template (e.g. leftover/partial infobox markup).

        :param text: The wikitext to process.
        :return: The processed wikitext.
        """
        pattern = re.compile(r"^[ \t]*\|(\s*image\d*\s*)=([^\n]*)", re.MULTILINE)

        fields_to_remove: list[str] = []

        for match in pattern.finditer(text):
            field_name = match.group(1).strip()
            filename = match.group(2).strip()

            if filename and self._image_service.image_exists(filename):
                continue

            fields_to_remove.append(field_name)

            number_match = re.match(r"^image(\d*)$", field_name, re.IGNORECASE)
            number = number_match.group(1) if number_match else ""
            fields_to_remove.append(f"caption{number}")

        # Suggestion: this regex fallback removes every |caption{number}= line (and every |image*=) across the entire text,
        # not just the lines belonging to the infobox whose image was confirmed missing. If the same caption2= / image field
        # appears in another template elsewhere, it gets deleted too. Scope the removal to the specific infobox block,
        # or at least only delete a caption whose paired image was actually missing.
        for field in fields_to_remove:
            field_pattern = re.compile(r"^[ \t]*\|\s*" + re.escape(field) + r"\s*=[^\n]*\n?", re.MULTILINE)
            text = field_pattern.sub("", text)

        return text

    def remove_missing_inline_images(self, text: str) -> str:
        """Remove inline ``[[File:...]]``/``[[Image:...]]`` images that don't exist.

        :param text: The wikitext to process.
        :return: The processed wikitext.
        """
        if not text:
            return text

        parsed = wtp.parse(text)

        # Two-pass: decide which links to drop before mutating any of them,
        # since removing an outer link would invalidate wikilinks nested
        # inside its caption.
        candidates = [link for link in parsed.wikilinks if link.title.strip().lower().startswith(("file:", "image:"))]
        to_remove = [
            link for link in candidates if not self._image_service.image_exists(link.title.split(":", 1)[1].strip())
        ]

        for link in to_remove:
            link.string = ""

        return str(parsed)

    def remove_missing_images(self, text: str) -> str:
        """Remove all missing images (both infobox and inline).

        :param text: The wikitext to process.
        :return: The processed wikitext with missing images removed.
        """
        text = self.remove_missing_infobox_images(text)
        text = self.remove_missing_inline_images(text)
        return text


__all__ = [
    "ImageExistenceChecker",
    "RemoveMissingImagesService",
]
