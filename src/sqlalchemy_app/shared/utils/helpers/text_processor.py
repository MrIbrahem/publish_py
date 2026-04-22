"""
Text processing utilities.

Mirrors: php_src/text_change.php

"""

import os

DoChangesToText1 = None
fix_one_page = None

try:
    from fix_refs import DoChangesToText1  # type: ignore
except ImportError:
    fix_refs_path = os.getenv("FIX_REFS_PY_PATH", "")
    if fix_refs_path and os.path.isdir(fix_refs_path):
        os.sys.path.insert(0, fix_refs_path)
        from fix_refs import DoChangesToText1  # type: ignore
        from fix_refs import fix_one_page  # type: ignore


def do_changes_to_text_with_settings(
    text: str,
    title: str,
    lang: str,
    source_title: str = "",
    mdwiki_revid: int = 0,
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


def do_changes_to_text(
    sourcetitle: str,
    title: str,
    text: str,
    lang: str,
    mdwiki_revid: str,
) -> str:
    """
    Apply text changes (e.g., fix references).

    Args:
        sourcetitle: Source page title
        title: Target page title
        text: Page text content
        lang: Target language code
        mdwiki_revid: MDWiki revision ID

    Returns:
        Modified text (currently unchanged)
    """
    if DoChangesToText1 is None:
        return text

    if not isinstance(text, str):
        return text

    if not text.strip():
        return text

    text = DoChangesToText1(
        text=text,
        title=title,
        lang=lang,
        source_title=sourcetitle,
        mdwiki_revid=mdwiki_revid,
    )
    return text
