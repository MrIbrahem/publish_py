"""
Template fixing utilities.

Port of ``src/Domain/Fixes/Templates/FixTemplatesFixture.php``.
"""

from __future__ import annotations

import wikitextparser as wtp
from ...parser import template_helpers as th

#: Infobox-like template name (lowercase) -> the parameter that should hold the page title.
_TITLE_PARAM_BY_TEMPLATE = {
    "drug box": "drug_name",
    "drugbox": "drug_name",
    "infobox drug": "drug_name",
    "infobox medical condition": "name",
    "infobox medical intervention": "name",
}


def add_missing_title(text: str, title: str, ljust: int = 17) -> str:
    """Add a missing title parameter to infobox templates.

    Only templates whose title parameter (``name``/``drug_name``, depending
    on the template) is missing or empty are touched; a template that
    already has a title is left untouched.

    :param text: The wikitext to process.
    :param title: The page title to add.
    :param ljust: Left-justify parameter names to this width when
        re-rendering a modified template (default 17), mirroring the
        PHP version's pretty-printing.
    :return: The wikitext with updated templates.
    """
    if not text:
        return text

    parsed = wtp.parse(text)

    for template in parsed.templates:
        name = th.strip_name(template).lower()

        param = _TITLE_PARAM_BY_TEMPLATE.get(name)
        if param is None:
            continue

        current_value = th.get_parameter(template, param, "")

        if not current_value.strip():
            th.set_parameter(template, param, title)
            # Re-render the whole template, matching the PHP version's
            # `toString(true, $ljust)` pretty-printing after modification.
            template.string = th.render_pretty(template, ljust)

    return str(parsed)


__all__ = [
    "add_missing_title",
]
