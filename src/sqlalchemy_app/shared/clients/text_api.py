import logging
import re

import requests

from ...config import settings

ALLOWED_WIKI_PROJECT = re.compile(r"^(?:[a-z0-9-]+\.wikipedia\.org|commons\.wikimedia\.org)$", re.IGNORECASE)

logger = logging.getLogger(__name__)


def get_wikitext(title, project="commons.wikimedia.org"):
    """
    Fetch raw wikitext of a page from Wikimedia projects.
    Args:
        title (str): Page title (e.g. 'Template:OWID/Parkinsons prevalence')
        project (str): Domain of wiki (default: commons.wikimedia.org)
    Returns:
        str: wikitext content or None if not found
    """

    if not ALLOWED_WIKI_PROJECT.fullmatch(project):
        logger.warning("Rejected unsupported wiki project: %s", project)
        return ""

    headers = {"User-Agent": settings.user_agent}
    api_url = f"https://{project}/w/api.php"
    # https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Yemen&rvprop=content&formatversion=2&rvslots=main&format=json
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "format": "json",
        "formatversion": "2",
        "rvslots": "*",
        "titles": title,
    }
    data = {}
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Error: get_wikitext : {e}")

    # data example: {"query": {"pages": [{"pageid": 350939, "ns": 0, "title": "Yemen", "revisions": [{"slots": {"main": {"contentmodel": "wikitext", "contentformat": "text/x-wiki", "content": ""}}}]}], "batchcomplete": True}, }

    pages = data.get("query", {}).get("pages", [])
    for page in pages:
        revs = page.get("revisions")
        if revs:
            return revs[0].get("slots", {}).get("main", {}).get("content") or ""

    return ""
