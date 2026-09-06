"""
Category removal utilities.

Port of ``src/Domain/Fixes/Structure/FixCategoriesFixture.php``.
"""

from __future__ import annotations

import wikitextparser as wtp


def remove_categories(text: str) -> str:
    """Remove all category tags from wikitext.

    :param text: The wikitext to process.
    :return: The wikitext with categories removed.

    """
    parsed = wtp.parse(text)
    for link in parsed.wikilinks:
        # The namespace prefix is the segment before the first colon. Strip
        # internal whitespace (e.g. "[[  Category  :  Medicine  ]]") and compare
        # case-insensitively.
        prefix = link.title.split(":", 1)[0].strip().lower()
        if prefix != "category":
            continue

        link.string = ""

    new_text = parsed.string.strip()
    return new_text


__all__ = [
    "remove_categories",
]
