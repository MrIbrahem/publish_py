"""Wikidata integration service.

Mirrors: php_src/bots/wd.php
"""

import json
import logging
from typing import Any

from ...config import settings
from ..sqlalchemy_db.services.qid_service import get_page_qid
from .oauth_client import post_params

logger = logging.getLogger(__name__)


def get_qid_for_mdtitle(title: str) -> str | None:
    """Get QID for an MDWiki title from the database.

    Args:
        title: MDWiki page title

    Returns:
        QID string or None if not found
    """
    qid_obj = get_page_qid(title)
    if qid_obj:
        return qid_obj.qid

    return None


def _link_it(
    qid: str,
    lang: str,
    sourcetitle: str,
    targettitle: str,
    access_key: str,
    access_secret: str,
) -> dict[str, Any]:
    """Create a sitelink on Wikidata.

    Args:
        qid: Wikidata item ID
        lang: Target language code
        sourcetitle: Source page title
        targettitle: Target page title
        access_key: OAuth access key
        access_secret: OAuth access secret

    Returns:
        API response dictionary
    """
    https_domain = f"https://{settings.wikidata_domain}"
    api_params = {
        "action": "wbsetsitelink",
        "linktitle": targettitle,
        "linksite": f"{lang}wiki",
    }

    if qid:
        api_params["id"] = qid
    else:
        api_params["title"] = sourcetitle
        api_params["site"] = "enwiki"

    try:
        response = post_params(api_params, https_domain, access_key, access_secret)
    except Exception as exc:
        logger.exception("Failed to call Wikidata API: %s", exc)
        return {}

    try:
        result = json.loads(response) if response else {}
    except json.JSONDecodeError:
        logger.error(f"Failed to parse Wikidata response: {response}")
        result = {}

    if "error" in result:
        logger.debug(f"Wikidata link error: {result['error']}")

    return result


def link_to_wikidata(
    sourcetitle: str,
    lang: str,
    user: str,
    targettitle: str,
    access_key: str,
    access_secret: str,
) -> dict[str, Any]:
    """Link a translated page to Wikidata.

    Args:
        sourcetitle: Source MDWiki page title
        lang: Target language code
        user: Username
        targettitle: Target page title
        access_key: OAuth access key
        access_secret: OAuth access secret

    Returns:
        Result dictionary with 'result' and 'qid' keys
    """
    qid = get_qid_for_mdtitle(sourcetitle) or ""

    if not access_key or not access_secret:
        return {"error": f"Access credentials not found for user: {user}", "qid": qid}

    link_result = _link_it(qid, lang, sourcetitle, targettitle, access_key, access_secret)
    link_result["qid"] = qid

    if link_result.get("success"):
        logger.debug("Wikidata link success")
        return {"result": "success", "qid": qid}

    return link_result
