"""
Wiki category parsing utilities.

Port of ``src/Domain/Parser/CategoryParser.php``. Category links are just
wikilinks in the ``Category:`` namespace, so this uses ``wikitextparser``'s
wikilink parsing instead of a hand-rolled regex.
"""

from __future__ import annotations

import wikitextparser as wtp


def get_categories(text: str) -> dict[str, str]:
    """Extract all categories from wikitext.

    :param text: The wikitext to parse.
    :return: A dict mapping category names (without the ``Category:`` prefix
        or trailing sort key) to their full ``[[Category:...]]`` tag text,
        e.g. ``{"Mental disorders": "[[Category:Mental disorders]]"}``.
    """
    if not text:
        return {}

    categories: dict[str, str] = {}

    for link in wtp.parse(text).wikilinks:
        title = link.title.strip()
        if not title.lower().startswith("category:"):
            continue

        # Drop the "Category:" namespace prefix; the sort key (anything
        # after "|") is already excluded from `.title` by wikitextparser.
        name = title.split(":", 1)[1].strip()

        # Suggestion: keying the result on the category name (sort key already stripped from .title) means two [[Category:X]]
        # links that differ only by sort key — e.g. [[Category:Foo]] and [[Category:Foo|Bar]] — collide, and the dict
        # overwrites the first. fix_categories.remove_categories then only removes one of them, silently leaving a category
        # behind. Consider using a list of (name, string) pairs (or keying on the full link.string) so every category
        # instance is captured and removed.
        categories[name] = link.string

    return categories


__all__ = [
    "get_categories",
]
