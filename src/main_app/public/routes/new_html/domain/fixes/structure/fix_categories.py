"""
Category removal utilities.

Port of ``src/Domain/Fixes/Structure/FixCategoriesFixture.php``.
"""

from __future__ import annotations

from domain.parser.category_parser import get_categories


def remove_categories(text: str) -> str:
    """Remove all category tags from wikitext.

    :param text: The wikitext to process.
    :return: The wikitext with categories removed.
    """
    for category_tag in get_categories(text).values():
        text = text.replace(category_tag, "")

    return text
