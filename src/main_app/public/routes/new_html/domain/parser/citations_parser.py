"""
Wiki citation parsing utilities.

Port of ``src/Domain/Parser/CitationsParser.php``. ``<ref>`` tags are parsed
with ``wikitextparser``'s tag parser instead of hand-rolled regexes, so
malformed/nested markup inside citations is handled correctly.

A "citation" dict has the same shape the PHP code used, for easy porting of
call sites::

    {
        "content": "...",   # inner text ("" for self-closing refs)
        "tag": "<ref ...>...</ref>",  # full original tag text
        "name": "some-name" or "",    # the `name` attribute, if any
        "options": {"name": "some-name", ...},  # all attributes (dict, not a raw string)
    }
"""

from __future__ import annotations

import wikitextparser as wtp
from wikitextparser import Tag


def _is_self_closing(tag: Tag) -> bool:
    """A self-closing ``<ref .../>`` (a "short citation") vs a full ``<ref>...</ref>``."""
    return tag.string.rstrip().endswith("/>")


def get_ref_name(tag: Tag) -> str:
    """Extract the ``name`` attribute from a ``<ref>`` tag.

    :param tag: A ``wikitextparser`` ``Tag`` object for a ``<ref>`` tag.
    :return: The trimmed name value, or an empty string if not present.
    """
    name = tag.get_attr("name")
    return name.strip() if name else ""


def _iter_ref_tags(text: str) -> list[Tag]:
    if not text:
        return []
    return wtp.parse(text).get_tags("ref")


def get_citations(text: str) -> list[dict]:
    """Get all full (non-self-closing) ``<ref>...</ref>`` citations.

    Equivalent of the PHP ``get_regex_citations()`` function.

    :param text: The text containing citations to extract.
    :return: A list of citation dicts (see module docstring).
    """
    citations = []
    for tag in _iter_ref_tags(text):
        if _is_self_closing(tag):
            continue
        citations.append(
            {
                "content": tag.contents,
                "tag": tag.string,
                "name": get_ref_name(tag),
                "options": dict(tag.attrs),
            }
        )
    return citations


def get_full_refs(text: str) -> dict[str, str]:
    """Get all full ref tags that have a ``name`` attribute.

    :param text: The text to parse.
    :return: A dict mapping ref names to their full ``<ref>...</ref>`` tag text.
    """
    full: dict[str, str] = {}
    for cite in get_citations(text):
        name = cite["name"]
        if not name:
            continue
        full[name] = cite["tag"]
    return full


def get_short_citations(text: str) -> list[dict]:
    """Get all short (self-closing) ``<ref name="..." />`` citations.

    :param text: The text to parse.
    :return: A list of citation dicts (see module docstring); ``content`` is
        always ``""`` for these.
    """
    citations = []
    for tag in _iter_ref_tags(text):
        if not _is_self_closing(tag):
            continue
        citations.append(
            {
                "content": "",
                "tag": tag.string,
                "name": get_ref_name(tag),
                "options": dict(tag.attrs),
            }
        )
    return citations


__all__ = [
    "get_ref_name",
    "get_citations",
    "get_full_refs",
    "get_short_citations",
]
