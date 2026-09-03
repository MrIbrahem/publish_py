"""
HTML post-processing utilities.

Currently only implements remove_data_parsoid.

TODO: Port the remaining helpers from the original PHP HtmlUtils:
      - del_div_error
      - fix_link_red
"""

from __future__ import annotations

import re
from bs4 import BeautifulSoup

def get_attrs(text: str) -> dict[str, str]:
    """Parse HTML attributes from a text string.

    @param text: The text containing attributes.
    @return: Dictionary of attribute name-value pairs.
    """
    text = f"<ref {text}>"
    attrfind_tolerant = r"((?<=[\'\"\s\/])[^\s\/>][^\s\/=>]*)(\s*=+\s*(\'[^\']*\'|\"[^\"]*\"|(?![\'\"])[^>\s]*))?(?:\s|\/(?!>))*"

    attrs = {}
    matches = re.finditer(attrfind_tolerant, text)

    for match in matches:
        attr_name = match.group(1).lower()
        # Extract attribute value if group 3 exists
        attr_value = match.group(3) if match.group(3) is not None else ""
        attrs[attr_name] = attr_value

    return attrs

def del_div_error(html: str) -> str:
    """
    TODO: implement this in Python from HtmlUtils.php
    """
    return html


def fix_link_red(html: str) -> str:
    """
    TODO: implement this in Python from HtmlUtils.php
    """
    return html

def remove_data_parsoid(html: str) -> str:
    """
    Remove data-parsoid attributes from HTML text.

    Mirrors the original PHP logic.
    """
    if not html:
        return ""

    # Replace all data-parsoid patterns using Regex
    html = re.sub(
        r'\s*data-parsoid\s*=\s*"{}"', "", html, flags=re.IGNORECASE | re.DOTALL
    )
    html = re.sub(
        r"\s*data-parsoid\s*=\s*'[^']*'",
        "",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    html = re.sub(
        r'\s*data-parsoid\s*=\s*"[^"]*"',
        "",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Match <a> tags and clean up remaining attributes
    html = clean_link_attributes(html)

    return html

def clean_link_attributes_new(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for a_tag in soup.find_all("a"):
        if "data-parsoid" in a_tag.attrs: # pyright: ignore[reportAttributeAccessIssue]
            del a_tag["data-parsoid"] # pyright: ignore[reportIndexIssue]

    return str(soup)

def clean_link_attributes(html: str):
    matches = list(
        re.finditer(r"<a([^>]*?)>(.+?)<\/a>", html, flags=re.IGNORECASE | re.DOTALL)
    )
    attrs_to_del = ["data-parsoid"]

    for match in matches:
        cite_text = match.group(0)
        options = match.group(1)
        content = match.group(2)

        if re.search(r"data-parsoid", options, flags=re.IGNORECASE):
            attrs = get_attrs(options)

            # Remove target attributes
            for attr in attrs_to_del:
                attrs.pop(attr, None)

            # Rebuild attribute string
            new_attrs = " ".join(f"{k}={v}" for k, v in attrs.items())
            new_cite_text = (
                f"<a {new_attrs}>{content}</a>" if new_attrs else f"<a>{content}</a>"
            )

            html = html.replace(cite_text, new_cite_text)

    return html


__all__ = [
    "remove_data_parsoid",
    "del_div_error",
    "fix_link_red",
]
