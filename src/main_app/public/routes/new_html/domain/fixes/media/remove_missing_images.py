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

import re
from typing import Protocol

import wikitextparser as wtp
from domain.parser import template_helpers as th

_IMAGE_PARAM_RE = re.compile(r"^image(\d*)$", re.IGNORECASE)


class ImageExistenceChecker(Protocol):
    """Equivalent of the PHP ``CommonsImageServiceInterface``."""

    def image_exists(self, filename: str) -> bool:
        """Return True if ``filename`` exists (e.g. on Wikimedia Commons)."""
        ...


class RemoveMissingImagesService:
    """Removes image references that don't exist on Commons from wikitext."""

    def __init__(self, image_service: ImageExistenceChecker):
        """
        :param image_service: Service used to check whether an image file exists.
        """
        self._image_service = image_service

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
