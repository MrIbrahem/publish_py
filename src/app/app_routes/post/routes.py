"""Post/Publish endpoint for Content Translation.

Mirrors: php_src/endpoints/post.php

This endpoint handles publishing translated pages to Wikipedia.
"""

import json
import logging
from typing import Any

from flask import Blueprint, Response, jsonify, request

from ...config import settings
from ...db.db_Pages import PagesDB
from ...db.db_publish_reports import ReportsDB
from ...helpers.cors import is_allowed
from ...helpers.files import to_do
from ...helpers.format import (
    determine_hashtag,
    format_title,
    format_user,
    make_summary,
)
from ...services.mediawiki_api import publish_do_edit
from ...services.revids_service import get_revid, get_revid_db
from ...services.text_processor import do_changes_to_text
from ...services.wikidata_client import link_to_wikidata
from ...users.store import get_user_token_by_username

bp_post = Blueprint("post", __name__)
logger = logging.getLogger(__name__)


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
    original_error: str,
) -> dict[str, Any]:
    """Retry Wikidata linking with fallback user credentials.

    Args:
        sourcetitle: Source page title
        lang: Target language code
        title: Target page title
        user: Original user
        original_error: Original error message

    Returns:
        Link result dictionary
    """
    logger.debug(f"get_csrftoken failed for user: {user}, retrying with Mr. Ibrahem")

    # Retry with "Mr. Ibrahem" credentials
    fallback_token = get_user_token_by_username("Mr. Ibrahem")

    if fallback_token is not None:
        fallback_access_key, fallback_access_secret = fallback_token.decrypted()

        link_result = link_to_wikidata(
            sourcetitle,
            lang,
            "Mr. Ibrahem",
            title,
            fallback_access_key,
            fallback_access_secret,
        )

        if "error" not in link_result:
            link_result["fallback_user"] = "Mr. Ibrahem"
            link_result["original_user"] = user
            logger.debug("Successfully linked using Mr. Ibrahem fallback credentials")

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

    try:
        link_result = link_to_wikidata(sourcetitle, lang, user, title, access_key, access_secret)

        # Check if the error is get_csrftoken failure and user is not already "Mr. Ibrahem"
        if link_result.get("error") == "get_csrftoken failed" and user != "Mr. Ibrahem":
            link_result["fallback"] = _retry_with_fallback_user(sourcetitle, lang, title, user, link_result["error"])
    except Exception as e:
        logger.error(f"Error linking to Wikidata: {e}")

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
        reports_db = ReportsDB(settings.db_data)
        reports_db.add(
            title=title,
            user=user,
            lang=lang,
            sourcetitle=sourcetitle,
            result=file_name,
            data=json.dumps(tab3),
        )

    return link_result


def _add_to_db(
    title: str,
    lang: str,
    user: str,
    wd_result: dict[str, Any],
    campaign: str,
    sourcetitle: str,
    mdwiki_revid: str,
) -> dict[str, Any]:
    """Add page to database.

    Args:
        title: Target page title
        lang: Target language code
        user: Username
        wd_result: Wikidata result
        campaign: Campaign name
        sourcetitle: Source page title
        mdwiki_revid: MDWiki revision ID

    Returns:
        Database operation result
    """
    # TODO: Implement campaign to category mapping
    cat = ""

    # Check if abuse filter warning was triggered
    to_users_table = "abusefilter-warning-39" in json.dumps(wd_result)

    pages_db = PagesDB(settings.db_data)
    return pages_db.insert_page_target(
        title=sourcetitle,
        tr_type="lead",
        cat=cat,
        lang=lang,
        user=user,
        target=title,
        to_users_table=to_users_table,
        mdwiki_revid=int(mdwiki_revid) if mdwiki_revid else None,
    )


def _process_edit(
    request_data: dict[str, Any],
    access_key: str,
    access_secret: str,
    text: str,
    user: str,
    tab: dict[str, Any],
) -> dict[str, Any]:
    """Process the edit request.

    Args:
        request_data: Original request data
        access_key: OAuth access key
        access_secret: OAuth access secret
        text: Page text content
        user: Username
        tab: Operation metadata

    Returns:
        Edit result dictionary
    """
    sourcetitle = tab["sourcetitle"]
    lang = tab["lang"]
    campaign = tab["campaign"]
    title = tab["title"]
    summary = tab["summary"]
    mdwiki_revid = tab.get("revid", "")

    # Prepare API parameters
    api_params = {
        "action": "edit",
        "title": title,
        "summary": summary,
        "text": text,
        "format": "json",
    }

    # Add captcha parameters if present
    if request_data.get("wpCaptchaId") and request_data.get("wpCaptchaWord"):
        api_params["wpCaptchaId"] = request_data["wpCaptchaId"]
        api_params["wpCaptchaWord"] = request_data["wpCaptchaWord"]

    # Perform the edit
    editit = publish_do_edit(api_params, lang, access_key, access_secret)

    success = editit.get("edit", {}).get("result", "")
    is_captcha = editit.get("edit", {}).get("captcha")

    tab["result"] = success

    if success == "Success":
        editit["LinkToWikidata"] = _handle_successful_edit(
            sourcetitle,
            lang,
            user,
            title,
            access_key,
            access_secret,
        )
        editit["sql_result"] = _add_to_db(title, lang, user, editit["LinkToWikidata"], campaign, sourcetitle, mdwiki_revid)
        to_do_file = "success"
    elif is_captcha:
        to_do_file = "captcha"
    else:
        to_do_file = _get_errors_file(editit, "errors")

    tab["result_to_cx"] = editit
    to_do(tab, to_do_file)

    # Insert to reports
    reports_db = ReportsDB(settings.db_data)
    reports_db.add(
        title=title,
        user=user,
        lang=lang,
        sourcetitle=sourcetitle,
        result=to_do_file,
        data=json.dumps(tab),
    )

    return editit


def _handle_no_access(user: str, tab: dict[str, Any]) -> Response:
    """Handle case when user has no access credentials.

    Args:
        user: Username
        tab: Operation metadata

    Returns:
        JSON error response
    """
    error = {"code": "noaccess", "info": "noaccess"}
    editit = {
        "error": error,
        "edit": {"error": error, "username": user},
        "username": user,
    }
    tab["result_to_cx"] = editit
    to_do(tab, "noaccess")

    # Insert to reports
    reports_db = ReportsDB(settings.db_data)
    reports_db.add(
        title=tab["title"],
        user=user,
        lang=tab["lang"],
        sourcetitle=tab["sourcetitle"],
        result="noaccess",
        data=json.dumps(tab),
    )

    return jsonify(editit)


@bp_post.route("/", methods=["POST", "OPTIONS"])
def index() -> Response:
    """Handle post/publish requests.

    Request Body (JSON):
        user: Username
        title: Target page title
        target: Target language code
        sourcetitle: Source page title
        text: Page content
        revid: Source revision ID (optional)
        campaign: Campaign name (optional)
        wpCaptchaId: Captcha ID (optional)
        wpCaptchaWord: Captcha answer (optional)

    Returns:
        JSON response with edit result
    """
    # Check CORS
    allowed = is_allowed()

    # Handle CORS preflight
    if request.method == "OPTIONS":
        if not allowed:
            return jsonify({"error": "CORS not allowed"}), 403
        response = Response("", status=200)
        response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    if not allowed:
        return jsonify({"error": "Access denied. Requests are only allowed from authorized domains."}), 403

    # Get request data
    request_data = request.get_json() or {}

    # Format inputs
    user = format_user(request_data.get("user", ""))
    title = format_title(request_data.get("title", ""))
    text = request_data.get("text", "")

    # Build operation metadata
    tab = {
        "title": title,
        "summary": "",
        "lang": request_data.get("target", ""),
        "user": user,
        "campaign": request_data.get("campaign", ""),
        "result": "",
        "edit": {},
        "sourcetitle": request_data.get("sourcetitle", ""),
    }

    # Get access credentials
    user_token = get_user_token_by_username(user)

    if user_token is None:
        response = _handle_no_access(user, tab)
        response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"
        return response, 403

    # Get credentials
    access_key, access_secret = user_token.decrypted()

    # Get revision ID
    revid = get_revid(tab["sourcetitle"])
    if not revid:
        revid = get_revid_db(tab["sourcetitle"])
    if not revid:
        tab["empty revid"] = "Can not get revid from all_pages_revids.json"
        revid = request_data.get("revid", "") or request_data.get("revision", "")
    tab["revid"] = revid

    # Generate summary
    hashtag = determine_hashtag(tab["title"], user)
    tab["summary"] = make_summary(revid, tab["sourcetitle"], tab["lang"], hashtag)

    # Apply text changes (fix references)
    newtext = do_changes_to_text(tab["sourcetitle"], tab["title"], text, tab["lang"], revid)
    if newtext:
        tab["fix_refs"] = "yes" if newtext != text else "no"
        text = newtext

    # Process the edit
    editit = _process_edit(request_data, access_key, access_secret, text, user, tab)

    response = jsonify(editit)
    response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"
    return response


__all__ = ["bp_post"]
