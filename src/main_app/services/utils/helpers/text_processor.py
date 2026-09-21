"""
Text processing utilities.

Mirrors: php_src/text_change.php

"""

from __future__ import annotations

import logging
from typing import Any

fix_one_page = None
logger = logging.getLogger(__name__)

try:
    from fix_refs import fix_one_page
except ImportError:
    fix_one_page = None
    logger.warning("fix_refs not found")


def do_changes_to_text_with_settings(
    text: str | Any,
    title: str,
    lang: str,
    source_title: str = "",
    mdwiki_revid: int | str = 0,
    move_dots: bool = True,
    expend_infobox: bool = True,
    add_en_lang: bool = False,
    add_category: bool = False,
) -> str:
    if fix_one_page is None:
        return text

    if not isinstance(text, str):
        return text

    if not text.strip():
        return text

    return fix_one_page(
        text=text,
        title=title,
        lang=lang,
        source_title=source_title,
        mdwiki_revid=mdwiki_revid,
        move_dots=move_dots,
        expend_infobox=expend_infobox,
        add_en_lang=add_en_lang,
        add_category=add_category,
    )


__all__ = [
    "do_changes_to_text_with_settings",
]
