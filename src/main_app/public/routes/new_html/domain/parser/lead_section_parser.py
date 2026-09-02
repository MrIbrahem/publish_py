"""
Lead section extraction utilities.

Port of ``src/Domain/Parser/LeadSectionParser.php``. The PHP version
manually split the text on the first ``==`` heading marker with a regex;
``wikitextparser`` already understands section structure, so the lead
section is simply ``sections[0]``.
"""

from __future__ import annotations

import wikitextparser as wtp


def get_lead_section(wikitext: str) -> str:
    """Get the lead section of wikitext (the content before the first heading).

    :param wikitext: The wikitext to process.
    :return: The lead section with a ``References`` section appended, or an
        empty string if there is no (non-empty) lead.
    """
    if not wikitext:
        return wikitext

    if "==" not in wikitext:
        return wikitext

    # sections[0] is always the "level 0" lead section, i.e. everything
    # before the first `==Heading==` marker.
    lead = str(wtp.parse(wikitext).sections[0]).strip()

    if not lead:
        return ""

    return lead + "\n==References==\n<references />"
