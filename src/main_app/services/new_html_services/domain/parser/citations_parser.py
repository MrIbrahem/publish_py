"""
Citation parser for WikiText reference tags
"""

from __future__ import annotations

import wikitextparser as wtp
from .citation import Citation

def get_all_citations(text: str) -> list[Citation]:
    """Extract all citations from text

    Args:
        text: Text containing citations

    Returns:
        List of Citation objects
    """
    citations = []
    parsed = wtp.parse(text)

    for tag in parsed.get_tags():
        if tag.name == "ref":
            # citations.append(Citation.from_text(tag.string))
            citations.append(Citation(tag))

    return citations


def get_full_refs(text: str) -> dict[str, str]:
    """Get mapping of citation names to their full reference tags

    Args:
        text: Text containing citations

    Returns:
        Dictionary mapping citation names to their full tags
    """
    full = {}
    citations = get_all_citations(text)

    for cite in citations:
        if cite.contents and cite.name:
            full[cite.name] = cite.tag

    return full


def get_short_refs(text: str) -> list[Citation]:
    """
    Extract short/empty citations (self-closing tags)

    Args:
        text: Text containing short citations

    Returns:
        List of Citation objects for short references
    """
    citations = []
    parsed = wtp.parse(text)
    for tag in parsed.get_tags():
        if tag.name == "ref" and not tag.contents:
            # citations.append(Citation.from_text(tag.string))
            citations.append(Citation(tag))

    return citations


__all__ = [
    "get_all_citations",
    "get_full_refs",
    "get_short_refs",
]
