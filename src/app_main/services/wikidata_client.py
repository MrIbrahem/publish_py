"""Wikidata integration service.

Mirrors: php_src/bots/wd.php
"""

import json
import logging
from typing import Any

import requests

from ..db import get_db
from .oauth_client import post_params

logger = logging.getLogger(__name__)


def get_qid_for_mdtitle(title: str) -> str | None:
    """Get QID for an MDWiki title from the database.

    Args:
        title: MDWiki page title

    Returns:
        QID string or None if not found
    """
    db = get_db()
    query = "SELECT qid FROM qids WHERE title = %s"

    try:
        result = db.fetch_query_safe(query, (title,))
        if result:
            return result[0].get("qid")
    except Exception as e:
        logger.error(f"Error fetching QID for {title}: {e}")

    return None


def get_title_info(targettitle: str, lang: str) -> dict[str, Any] | None:
    """Get page information from Wikipedia API.

    Args:
        targettitle: Target page title
        lang: Language code

    Returns:
        Page info dictionary or None if not found
    """
    params = {
        "action": "query",
        "format": "json",
        "titles": targettitle,
        "utf8": 1,
        "formatversion": "2",
    }
    url = f"https://{lang}.wikipedia.org/w/api.php"

    try:
        response = requests.get(url, params=params, timeout=30)
        result = response.json()
        logger.debug(f"GetTitleInfo result: {result}")
        pages = result.get("query", {}).get("pages", [])
        if pages:
            return pages[0]
    except Exception as e:
        logger.error(f"GetTitleInfo error: {e}")

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
    https_domain = "https://www.wikidata.org"
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

    response = post_params(api_params, https_domain, access_key, access_secret)

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
