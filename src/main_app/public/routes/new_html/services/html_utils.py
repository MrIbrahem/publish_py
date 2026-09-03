"""
HTML post-processing utilities.

Currently only implements remove_data_parsoid.

TODO: Port the remaining helpers from the original PHP HtmlUtils:
      - fix_link_red
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag

def del_div_error(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Directly match and remove <div> elements containing class="error"
    for div_tag in soup.find_all("div", class_="error"):
        div_tag.decompose()
    return str(soup)

def fix_link_red(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    attrs_to_del = ["typeof", "data-mw-i18n", "class"]

    # <a rel="mw:ExtLink" href="//en.wikipedia.org/w/index.php?title=Video:Pelvic_binder&amp;veaction=edit" class="external text"><span class="mw-ui-button mw-ui-progressive">Edit with VisualEditor</span></a>

    # if link has Edit with VisualEditor del it
    for a_tag in soup.find_all("a"):
        if not isinstance(a_tag, Tag):
            continue

        if "Edit with VisualEditor" in a_tag.get_text():
            a_tag.decompose()

    # data-parsoid="{}"
    for a_tag in soup.find_all("a"):
        if not isinstance(a_tag, Tag):
            continue

        typeof = a_tag.get("typeof", "")
        href = a_tag.get("href", "")

        if typeof and "mw:LocalizedAttrs" in typeof:
            href_str = str(href)
            if href and "action=edit" in href_str:
                new_href = re.sub(r"\?action=edit.*?", "", href_str)
                new_href = new_href.replace("&amp;redlink=1", "")
                new_href = new_href.replace("&redlink=1", "")

                a_tag["href"] = new_href

                for attr in attrs_to_del:
                    if attr in a_tag.attrs:
                        del a_tag[attr]

    return str(soup)


def remove_data_parsoid(html: str) -> str:
    """
    Clean link attributes by removing 'data-parsoid' attributes from HTML elements.

    This function parses the provided HTML string, iterates over all tags,
    and removes the 'data-parsoid' attribute if it exists.

    Args:
        html (str): The HTML string to be cleaned.

    Returns:
        str: The cleaned HTML string with 'data-parsoid' attributes removed.
    """
    soup = BeautifulSoup(html, "html.parser")
    for a_tag in soup.find_all(True):
        if not isinstance(a_tag, Tag):
            continue

        if "data-parsoid" in a_tag.attrs:
            del a_tag["data-parsoid"]

    return str(soup)


__all__ = [
    "remove_data_parsoid",
    "del_div_error",
    "fix_link_red",
]
