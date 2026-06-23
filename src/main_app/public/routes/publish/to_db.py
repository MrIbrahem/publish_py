""" """

import json
import logging
from typing import Any

from ....db.models import PageRecord, UserPageRecord
from ....db.services.content import get_campaign_category
from ....db.services.pages import (
    find_page_record,
    find_user_page_record,
    insert_page_target,
    insert_user_page_target,
    set_page_target,
    set_user_page_target,
)

logger = logging.getLogger(__name__)


def find_exists_or_update_page(
    sourcetitle: str,
    lang: str,
    user: str,
    target: str,
) -> bool:
    orm_obj: PageRecord | None = find_page_record(sourcetitle, lang, user)
    if orm_obj:
        return set_page_target(orm_obj, target)
    return False


def find_exists_or_update_user_page(
    sourcetitle: str,
    lang: str,
    user: str,
    target: str,
) -> bool:
    orm_obj: UserPageRecord | None = find_user_page_record(sourcetitle, lang, user)
    if orm_obj:
        return set_user_page_target(orm_obj, target)
    return False


def add_to_db(
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

    if isinstance(words, str):
        words = int(words)

    # Validate required fields
    if not user or not sourcetitle or not lang:
        return {
            "use_user_sql": False,
            "to_users_table": to_users_table,
            "one_empty": {"title": sourcetitle, "lang": lang, "user": user},
        }

    result: dict[str, Any] = {
        "use_user_sql": to_users_table,
        "to_users_table": to_users_table,
    }

    # Check if exists and update if needed
    if to_users_table:
        exists = find_exists_or_update_user_page(sourcetitle, lang, user, target)
    else:
        exists = find_exists_or_update_page(sourcetitle, lang, user, target)

    if exists:
        result["exists"] = "already_in"
        return result

    md_revid = int(mdwiki_revid) if mdwiki_revid else None

    if to_users_table:
        # Insert new record
        add_done = insert_user_page_target(
            sourcetitle=sourcetitle,
            translate_type=translate_type,
            cat=cat,
            lang=lang,
            user=user,
            target=target,
            mdwiki_revid=md_revid,
            word=words,
        )
    else:
        # Insert new record
        add_done = insert_page_target(
            sourcetitle=sourcetitle,
            translate_type=translate_type,
            cat=cat,
            lang=lang,
            user=user,
            target=target,
            mdwiki_revid=md_revid,
            word=words,
        )

    result["execute_query"] = add_done is True
    return result


__all__ = [
    "add_to_db",
]
