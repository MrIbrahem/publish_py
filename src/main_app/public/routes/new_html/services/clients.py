"""
External API clients for the new_html module.

- MdwikiApi: fetch wikitext + revision id
- TransformApi: wikitext → HTML

# TODO: Port CommonsImageService if/when removeMissingImages is implemented.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import requests

from .....config.main_settings import get_settings

logger = logging.getLogger(__name__)

def normalize_title_for_url(title: str) -> str:
    """
    doesn't normalize the title. Here the title is only replace("/", "%2F"), whereas MdwikiApi.get_wikitext
    also replaces spaces with underscores. Multi-word titles will build a malformed REST URL and the
    transform will fail. Reuse the same encoding as the fetch path.
    """
    title = title.replace(" ", "_")
    title = title.replace("/", "%2F")
    return title


def _get_user_agent() -> str:
    """Return the project-wide User-Agent."""
    settings = get_settings()
    return getattr(
        settings.other,
        "user_agent",
        ("WikiProjectMed Translation Dashboard/1.0 (https://medwiki.toolforge.org/; tools.mdwikicx@toolforge.org)"),
    )


def _request(
    url: str,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    json_data: dict[str, Any] | None = None,
    timeout: float = 15.0,
) -> dict[str, Any]:
    """
    Low-level HTTP helper.

    Returns a normalized dict:
    {
        "output": str,
        "error": str,
        "error_code": str,
        "http_code": int,
    }
    """
    result = {
        "output": "",
        "error": "",
        "error_code": "",
        "http_code": 0,
    }

    headers = {"User-Agent": _get_user_agent()}

    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            params=params,
            data=data,
            json=json_data,
            headers=headers,
            timeout=timeout,
        )
        result["http_code"] = response.status_code

        if response.status_code != 200:
            result["error"] = "HTTP_ERROR"
            result["error_code"] = str(response.status_code)
            logger.warning("HTTP %s for URL: %s", response.status_code, url)
            return result

        result["output"] = response.text

    except requests.Timeout:
        result["error"] = "Request timed out"
        result["error_code"] = "TIMEOUT"
        logger.error("Timeout while requesting: %s", url)
    except Exception as exc:
        result["error"] = str(exc)
        result["error_code"] = "REQUEST_ERROR"
        logger.error("Request failed for %s: %s", url, exc)

    return result


class MdwikiApi:
    """Fetch wikitext and revision ID from mdwiki.org."""

    REST_BASE = "https://mdwiki.org/w/rest.php/v1"
    API_BASE = "https://mdwiki.org/w/api.php"

    def get_wikitext(self, title: str) -> tuple[str, str, str]:
        """
        Return (source, revid, error).
        Follows #REDIRECT if present.
        """
        source, revid, error = self._fetch_rest(title)

        # Follow redirect
        if source:
            match = re.search(r"#REDIRECT\s*\[\[(.*?)\]\]", source, re.IGNORECASE)
            if match:
                redirect_title = match.group(1).strip()
                logger.info("Redirecting to: %s", redirect_title)
                source, revid, error = self._fetch_rest(redirect_title)

        return source, str(revid) if revid else "", error

    def _fetch_rest(self, title: str) -> tuple[str, str, str]:
        title_encoded = normalize_title_for_url(title)

        url = f"{self.REST_BASE}/page/{title_encoded}"

        response = _request(url, method="GET")
        if response["error"] or not response["output"]:
            # Fallback to Action API
            return self._fetch_action_api(title)

        try:
            data = json.loads(response["output"])
            source = data.get("source", "")
            revid = data.get("latest", {}).get("id", "")
            return source, str(revid), ""
        except Exception as exc:
            logger.error("Failed to parse MDWiki REST response: %s", exc)
            return self._fetch_action_api(title)

    def _fetch_action_api(self, title: str) -> tuple[str, str, str]:
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": title,
            "utf8": 1,
            "formatversion": "2",
            "rvprop": "content|ids",
        }
        response = _request(self.API_BASE, method="GET", params=params)

        if response["error"] or not response["output"]:
            return "", "", response.get("error") or "Empty response"

        try:
            data = json.loads(response["output"])
            pages = data.get("query", {}).get("pages", [])
            if not pages:
                return "", "", "No pages found"

            revisions = pages[0].get("revisions", [])
            if not revisions:
                return "", "", "No revisions found"

            source = revisions[0].get("content", "")
            revid = revisions[0].get("revid", "")
            return source, str(revid), ""
        except Exception as exc:
            logger.error("Failed to parse MDWiki Action API response: %s", exc)
            return "", "", str(exc)


class TransformApi:
    """Convert wikitext to HTML using English Wikipedia REST API."""

    def convert(self, wikitext: str, title: str) -> dict[str, str]:
        """
        Returns {"result": html} or {"error": message}.
        """
        if not wikitext:
            return {"error": "Empty wikitext"}

        settings = get_settings()
        base_url = settings.new_html.transform_base_url

        title_encoded = normalize_title_for_url(title)
        url = f"{base_url}/transform/wikitext/to/html/{title_encoded}"

        response = _request(
            url,
            method="POST",
            data={"wikitext": wikitext},
            timeout=30.0,
        )

        if response["error"] or not response["output"]:
            logger.error("Transform API failed for title: %s", title)
            return {"error": response.get("error") or "Empty response"}

        html = response["output"]

        if "Wikimedia Error" in html:
            return {"error": "Wikipedia API returned an error"}

        if "<html" not in html.lower():
            return {"error": "Invalid HTML returned"}

        return {"result": html}
