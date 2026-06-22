"""

"""

import json
import logging
from typing import Any

from ....db.models import PageRecord, UserPageRecord
from ....db.services.content import get_campaign_category
from ....db.services.pages import (
    find_page_record,
    insert_page_target,
    insert_user_page_target,
    set_page_target,
    set_user_page_target,
    find_user_page_record,
)
logger = logging.getLogger(__name__)

def find_exists_or_update_page(sourcetitle, lang, user, target):
    orm_obj: PageRecord | None = find_page_record(sourcetitle, lang, user)
    if orm_obj:
        exists = True
        exists = set_page_target(orm_obj, target)
    return exists


def find_exists_or_update_user_page(sourcetitle, lang, user, target):
    orm_obj: UserPageRecord | None = find_user_page_record(sourcetitle, lang, user)
    if orm_obj:
        exists = True
        exists = set_user_page_target(orm_obj, target)
    return exists


def _add_to_db(
    target: str,
    lang: str,
    user: str,
    wd_result: dict[str, Any],
    campaign: str,
    sourcetitle: str,
    mdwiki_revid: str,
    translate_type: str = "lead",
    words: int = 0,
) -> dict[str, Any]:
    """Add page to database.

    Args:
        target: Target page title
        lang: Target language code
        user: Username
        wd_result: Wikidata result
        campaign: Campaign name
        sourcetitle: Source page title
        mdwiki_revid: MDWiki revision ID
        translate_type: Translation type
        words: Article words

    Returns:
        Database operation result
    """
    # Get category from campaign using database lookup
    # This mirrors the PHP retrieveCampaignCategories() function
    cat_object = get_campaign_category(campaign)
    cat = cat_object.category if cat_object else ""

    # Check if abuse filter warning was triggered
    to_users_table = "abusefilter-warning-39" in json.dumps(wd_result)

    if not to_users_table:
        user_t = user.replace("User:", "").replace("user:", "")
        if user_t in target:
            to_users_table = True

    # Normalize inputs
    sourcetitle = sourcetitle.replace("_", " ")
    target = target.replace("_", " ")
    user = user.replace("_", " ")

    # Validate required fields
    if not user or not sourcetitle or not lang:
        return {
            "use_user_sql": False,
            "to_users_table": to_users_table,
            "one_empty": {"title": sourcetitle, "lang": lang, "user": user},
        }

    return insert_to_db(
        target,
        lang,
        user,
        sourcetitle,
        mdwiki_revid,
        cat,
        words,
        to_users_table,
        translate_type=translate_type,
    )


def insert_to_db(
    target,
    lang,
    user,
    sourcetitle,
    mdwiki_revid,
    cat,
    word: str | int,
    to_users_table,
    translate_type: str = "lead",
) -> dict[str, Any]:
    return insert_to_db_2(
        sourcetitle=sourcetitle,
        translate_type=translate_type,
        cat=cat,
        lang=lang,
        user=user,
        target=target,
        use_user_sql=to_users_table,
        mdwiki_revid=int(mdwiki_revid) if mdwiki_revid else None,
        word=word,
    )


def insert_to_db_2(
    sourcetitle: str,
    lang: str,
    user: str,
    translate_type: str,
    cat: str,
    target: str,
    use_user_sql: bool = False,
    mdwiki_revid: int | None = None,
    word: int | str = 0,
) -> dict[str, Any]:
    """
    Insert a page target record.

    Mirrors: php_src/bots/sql/db_pages.php InsertPageTarget()

    Args:
        sourcetitle: Page title
        translate_type: Translation type
        cat: Category
        lang: Target language
        user: Username
        target: Target page title
        use_user_sql: Whether to insert to pages_users table
        mdwiki_revid: MDWiki revision ID
        word: Word count

    Returns:
        Dictionary with operation result
    """
    result: dict[str, Any] = {
        "use_user_sql": use_user_sql,
        "to_users_table": use_user_sql,
    }

    # Check if exists and update if needed
    if use_user_sql:
        exists = find_exists_or_update_user_page(sourcetitle, lang, user, target)
    else:
        exists = find_exists_or_update_page(sourcetitle, lang, user, target)

    if exists:
        result["exists"] = "already_in"
        return result

    table_sql = "pages_users" if use_user_sql else "pages"

    if isinstance(word, str):
        word = int(word)

    if table_sql == "pages":
        # Insert new record
        add_done = insert_page_target(
            sourcetitle=sourcetitle,
            translate_type=translate_type,
            cat=cat,
            lang=lang,
            user=user,
            target=target,
            mdwiki_revid=mdwiki_revid,
            word=word,
        )
    else:
        # Insert new record
        add_done = insert_user_page_target(
            sourcetitle=sourcetitle,
            translate_type=translate_type,
            cat=cat,
            lang=lang,
            user=user,
            target=target,
            mdwiki_revid=mdwiki_revid,
            word=word,
        )

    result["execute_query"] = add_done is True

    return result

__all__ = [
    "_add_to_db",
]
