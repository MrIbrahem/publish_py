"""
Post/Publish endpoint worker for Content Translation.
"""

import json
import logging
from typing import Any

from ....config import settings
from ....db.models import LanguageSettingRecord
from ....db.services.config import get_language_setting_by_code
from ....db.services.reports import add_report
from ....db.services.users import get_user_token_by_username
from ....shared.clients import (
    get_revid,
    get_revid_db,
    get_title_info,
    link_to_wikidata,
    publish_do_edit,
)
from ....shared.utils.helpers import (
    determine_hashtag,
    do_changes_to_text_with_settings,
    get_word_count,
    make_summary,
    to_do,
)
from .to_db import add_to_db

logger = logging.getLogger(__name__)


def load_language_settings(lang: str) -> LanguageSettingRecord:
    """Load language settings for the given language.

    Args:
        lang: Language code

    Returns:
        LanguageSettingRecord object
    """
    return get_language_setting_by_code(lang) or LanguageSettingRecord()


def _get_revid(sourcetitle) -> str:
    revid = get_revid(sourcetitle)

    if not revid:
        revid = get_revid_db(sourcetitle)

    return revid


def shouldAddedToWikidata(lang, title) -> bool:
    """ """
    page_information = get_title_info(title, lang)
    if not page_information:
        return False

    page_namespace = page_information.get("ns", None)

    if page_namespace == 2:
        # skip link to wd for user pages
        return False

    return True


def _get_errors_file(editit: dict[str, Any], placeholder: str) -> str:
    """Determine the appropriate error file based on error content.

    Args:
        editit: Edit result dictionary
        placeholder: Default placeholder value

    Returns:
        Error file name
    """
    to_do_file = placeholder
    errs_main = [
        "protectedpage",
        "titleblacklist",
        "ratelimited",
        "editconflict",
        "spam filter",
        "abusefilter",
        "mwoauth-invalid-authorization",
    ]
    errs_wd = {
        "Links to user pages": "wd_user_pages",
        "get_csrftoken": "wd_csrftoken",
        "protectedpage": "wd_protectedpage",
    }

    errs = errs_main if placeholder == "errors" else errs_wd
    c_text = json.dumps(editit)

    if isinstance(errs, list):
        for err in errs:
            if err in c_text:
                to_do_file = err
                break
    else:
        for err, file_name in errs.items():
            if err in c_text:
                to_do_file = file_name
                break

    return to_do_file


def _retry_with_fallback_user(
    sourcetitle: str,
    lang: str,
    title: str,
    user: str,
) -> dict[str, Any]:
    """Retry Wikidata linking with fallback user credentials.

    Args:
        sourcetitle: Source page title
        lang: Target language code
        title: Target page title
        user: Original user

    Returns:
        Link result dictionary
    """
    fallback_user = settings.users.fallback_user
    logger.debug(f"get_csrftoken failed for user: {user}, retrying with {fallback_user}")

    # Retry with fallback user credentials
    fallback_token = get_user_token_by_username(fallback_user)

    if fallback_token is not None:
        fallback_access_key, fallback_access_secret = fallback_token.decrypted()

        link_result = link_to_wikidata(
            sourcetitle,
            lang,
            fallback_user,
            title,
            fallback_access_key,
            fallback_access_secret,
        )

        if "error" not in link_result:
            link_result["fallback_user"] = fallback_user
            link_result["original_user"] = user
            logger.debug(f"Successfully linked using {fallback_user} fallback credentials")

        return link_result

    return {}


def _handle_successful_edit(
    sourcetitle: str,
    lang: str,
    user: str,
    title: str,
    access_key: str,
    access_secret: str,
) -> dict[str, Any]:
    """Handle post-edit operations for successful edits.

    Args:
        sourcetitle: Source page title
        lang: Target language code
        user: Username
        title: Target page title
        access_key: OAuth access key
        access_secret: OAuth access secret

    Returns:
        Wikidata link result
    """
    link_result: dict[str, Any] = {}

    if not shouldAddedToWikidata(lang, title):
        # skip link to wd for user pages
        return {"error": "skip link to wd for user pages"}

    link_result = link_to_wikidata(sourcetitle, lang, user, title, access_key, access_secret)

    # Check if the error is get_csrftoken failure and user is not already the fallback user
    fallback_user = settings.users.fallback_user
    if link_result.get("error") == "get_csrftoken failed" and user != fallback_user:
        link_result["fallback"] = _retry_with_fallback_user(sourcetitle, lang, title, user)

    if "error" in link_result:
        tab3 = {
            "error": link_result["error"],
            "qid": link_result.get("qid", ""),
            "title": title,
            "sourcetitle": sourcetitle,
            "fallback": link_result.get("fallback", ""),
            "lang": lang,
            "username": user,
        }
        file_name = _get_errors_file(link_result.get("error", {}), "wd_errors")
        to_do(tab3, file_name)

        # Insert to reports
        add_report(
            title=title,
            user=user,
            lang=lang,
            sourcetitle=sourcetitle,
            result=file_name,
            data=json.dumps(tab3),
        )

    return link_result


def load_to_do_file(editit) -> str:
    if editit.get("edit", {}).get("result", "") == "Success":
        to_do_file = "success"
    elif editit.get("edit", {}).get("captcha"):
        to_do_file = "captcha"
    else:
        to_do_file = _get_errors_file(editit, "errors")

    return to_do_file


def _process_edit(
    access_key: str,
    access_secret: str,
    text: str,
    tab: dict[str, Any],
) -> dict[str, Any]:
    """Process the edit request.

    Args:
        access_key: OAuth access key
        access_secret: OAuth access secret
        text: Page text content
        tab: Operation metadata

    Returns:
        Edit result dictionary
    """
    sourcetitle = tab["sourcetitle"]
    lang = tab["lang"]
    campaign = tab["campaign"]
    title = tab["title"]
    user = tab["user"]
    translate_type = tab["translate_type"]

    # Get word count (mirrors PHP $tab['words'] = $Words_table[$title] ?? 0)
    tab["words"] = get_word_count(sourcetitle)

    # Get revision ID
    mdwiki_revid = _get_revid(sourcetitle)

    if not mdwiki_revid:
        tab["empty revid"] = "Can not get revid from all_pages_revids.json"
        mdwiki_revid = tab.get("request_revid", "")

    tab["revid"] = mdwiki_revid

    # Apply text changes (fix references)

    language_setting = load_language_settings(lang)

    newtext = do_changes_to_text_with_settings(
        text=text,
        title=title,
        lang=lang,
        source_title=sourcetitle,
        mdwiki_revid=mdwiki_revid,
        move_dots=bool(language_setting.move_dots),
        expend_infobox=bool(language_setting.expend),
        add_en_lang=bool(language_setting.add_en_lang),
        # add_category=add_category,
    )

    if newtext:
        tab["fix_refs"] = "yes" if newtext != text else "no"
        text = newtext

    # Generate summary
    hashtag = determine_hashtag(tab["title"], user)

    tab["summary"] = make_summary(mdwiki_revid, sourcetitle, lang, hashtag)

    # Prepare API parameters
    api_params = {
        "action": "edit",
        "title": title,
        "summary": tab["summary"],
        "text": text,
        "format": "json",
    }

    # Add captcha parameters if present
    if tab.get("wp_captcha_params"):
        api_params.update(tab["wp_captcha_params"])

    # Perform the edit
    editit = publish_do_edit(api_params, lang, access_key, access_secret)

    success = editit.get("edit", {}).get("result", "")

    tab["result"] = success

    if success == "Success":
        link_to_wd = _handle_successful_edit(
            sourcetitle,
            lang,
            user,
            title,
            access_key,
            access_secret,
        )

        sql_result = add_to_db(
            title,
            lang,
            user,
            link_to_wd,
            campaign,
            sourcetitle,
            mdwiki_revid,
            translate_type=translate_type,
            words=tab["words"],
        )

        editit["LinkToWikidata"] = link_to_wd
        editit["sql_result"] = sql_result

    to_do_file = load_to_do_file(editit)

    tab["result_to_cx"] = editit
    to_do(tab, to_do_file)

    add_report(
        title=title,
        user=user,
        lang=lang,
        sourcetitle=sourcetitle,
        result=to_do_file,
        data=json.dumps(tab),
    )

    return editit


def _handle_no_access(tab: dict[str, Any]) -> dict:
    """Handle case when user has no access credentials.

    Args:
        tab: Operation metadata

    Returns:
        JSON error response
    """
    user = tab["user"]
    error = {"code": "noaccess", "info": "noaccess"}
    editit = {
        "error": error,
        "edit": {"error": error, "username": user},
        "username": user,
    }
    tab["result_to_cx"] = editit
    to_do(tab, "noaccess")

    add_report(
        title=tab["title"],
        user=user,
        lang=tab["lang"],
        sourcetitle=tab["sourcetitle"],
        result="noaccess",
        data=json.dumps(tab),
    )

    return editit


__all__ = [
    "_get_revid",
    "_handle_no_access",
    "_process_edit",
]
