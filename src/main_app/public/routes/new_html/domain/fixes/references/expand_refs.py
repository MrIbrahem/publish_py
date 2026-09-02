"""
Reference expansion utilities.

Port of ``src/Domain/Fixes/References/ExpandRefsFixture.php``.

The PHP version called into an ``Infrastructure\\Debug\\test_print`` helper
that isn't part of the parser/fixes source provided for conversion; it's
replaced here with the standard ``logging`` module, which serves the same
purpose (optional debug tracing) without depending on unavailable
infrastructure code.
"""

from __future__ import annotations

import logging

from domain.parser.citations_parser import get_full_refs, get_short_citations

logger = logging.getLogger(__name__)


def expand_refs(first: str, alltext: str) -> str:
    """Expand short references by finding their full definitions elsewhere in the page.

    :param first: The lead section text containing short refs.
    :param alltext: The full page text containing full ref definitions. If
        empty, ``first`` is used instead.
    :return: The text with short refs expanded to their full ref definition.
    """
    if not alltext:
        alltext = first

    logger.debug("expand_refs")

    all_page_full_refs = get_full_refs(alltext)
    lead_full_refs = get_full_refs(first)
    lead_short_refs = get_short_citations(first)

    logger.debug("lead_short_refs: %r", lead_short_refs)

    for cite in lead_short_refs:
        name = cite.get("name", "")
        short_tag = cite.get("tag", "")

        if not name or not short_tag:
            continue

        if name in lead_full_refs:
            continue

        full_ref = all_page_full_refs.get(name, "")

        if full_ref:
            logger.debug(
                "expand_refs: name=(%s), short_tag=(%s), full_ref=(%s)",
                name,
                short_tag,
                full_ref,
            )
            first = first.replace(short_tag, full_ref)

    return first
