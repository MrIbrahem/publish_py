"""
Empty reference handling utilities.

Port of ``src/Domain/Fixes/References/DeleteEmptyRefsFixture.php``.
"""

from __future__ import annotations

from domain.parser.citations_parser import get_full_refs, get_short_refs


def del_empty_refs(text: str) -> str:
    """
    Delete empty short refs, or expand them with their full ref definition.

    For each short (self-closing) ``<ref name="x" />`` tag: if a full
    ``<ref name="x">...</ref>`` definition exists elsewhere in ``text``, the
    short tag is replaced with that full definition (unless the full
    definition is already present verbatim). Otherwise the short tag is
    removed entirely.

    :param text: The text containing short refs.
    :return: The text with empty refs removed and expandable refs replaced.
    """
    full_refs = get_full_refs(text)
    short_refs = get_short_refs(text)

    for cite in short_refs:
        name = cite["name"]
        short_tag = cite["tag"]

        full_tag = full_refs.get(name)
        if full_tag:
            # Don't duplicate the full ref if it's already present in `text`.
            if full_tag not in text:
                text = text.replace(short_tag, full_tag)
        else:
            text = text.replace(short_tag, "")

    return text


__all__ = [
    "del_empty_refs",
]
