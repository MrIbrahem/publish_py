"""
Infobox expansion functions
"""

from __future__ import annotations

import logging

import wikitextparser as wtp

logger = logging.getLogger(__name__)


def expend_all_templates(text: str) -> str:
    parsed = wtp.parse(text)
    for template in parsed.templates:
        # ---
        if not template:
            continue
        # ---
        new_line_value = "\n" if template.string.count("\n") > 1 else ""
        # ---
        template_name = str(template.normal_name()).strip()
        template.name = f"{template_name}{new_line_value}"
        # ---
        for arg in template.arguments:
            param = arg.name.strip()
            value = arg.value.strip()
            # ---
            if param != arg.name:
                arg.name = param
            arg.value = f"{value}{new_line_value}"
    # ---
    return parsed.string


__all__ = [
    "expend_all_templates",
]
