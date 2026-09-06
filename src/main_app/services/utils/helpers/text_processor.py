"""
Text processing utilities.

Mirrors: php_src/text_change.php

"""

from __future__ import annotations

import os
import sys
from typing import Any

fix_one_page = None

try:
    from fix_refs import fix_one_page  # type: ignore
except ImportError:
    fix_refs_path = os.getenv("FIX_REFS_PY_PATH", "")
    if fix_refs_path and os.path.isdir(fix_refs_path):
        sys.path.insert(0, fix_refs_path)
        from fix_refs import fix_one_page  # type: ignore


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
