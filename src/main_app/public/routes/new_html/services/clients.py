"""
External API clients for the new_html module.

- MdwikiApi: fetch wikitext + revision id
- TransformApi: wikitext → HTML

# TODO: Port ImageExistenceChecker if/when remove_missing_images is implemented.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import requests

from .....config.main_settings import settings

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

class HttpClientService:

    @staticmethod
    def request(
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

        headers = {"User-Agent": settings.other.user_agent}

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
        except requests.Timeout:
            result["error"] = "Request timed out"
            result["error_code"] = "TIMEOUT"
            logger.error("Timeout while requesting: %s", url)
            return result
        except Exception as exc:
            result["error"] = str(exc)
            result["error_code"] = "REQUEST_ERROR"
            logger.error("Request failed for %s: %s", url, exc)
            return result

        output = response.text
        result["output"] = output
        result["http_code"] = response.status_code

        if response.status_code != 200:
            logging.error("HttpClientService: API returned HTTP %s", response.status_code)
            result["error"] = "HTTP_ERROR"
            result["error_code"] = str(response.status_code)

            # check Cloudflare protection
            if isinstance(output, str) and "Just a moment..." in output:
                logging.error( "HttpClientService: Cloudflare protection detected" )
                logger.error(
                    "Cloudflare protection detected: 'Just a moment...' page returned"
                )
                result["error"] = "CLOUDFLARE_PROTECTION"

            else:
                logger.error(repr(output))

            result["output"] = ""
            return result

        return result


def request(
    url: str,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    json_data: dict[str, Any] | None = None,
    timeout: float = 15.0,
) -> dict[str, Any]:
    return HttpClientService.request(
        url=url,
        method=method,
        params=params,
        data=data,
        json_data=json_data,
        timeout=timeout,
    )

class MdwikiApi:
    """
    Service for fetching wikitext content from mdwiki.org

    https://mdwiki.org/w/rest.php/v1/page/Sympathetic_crashing_acute_pulmonary_edema/html
    https://mdwiki.org/w/rest.php/v1/revision/1420795/html

    """

    REST_BASE = "https://mdwiki.org/w/rest.php/v1"
    API_BASE = "https://mdwiki.org/w/api.php"
    def __init__(self):
        # Fallback to Action API
        self.fallback_to_action_api = False

    def _fetch_rest(self, title: str) -> tuple[str, str, str]:
        title_encoded = normalize_title_for_url(title)

        url = f"{self.REST_BASE}/page/{title_encoded}"

        response = _request(url, method="GET")

        output = response.get("output")
        error = response.get("error")

        if response["error"] or not output:
            logger.error("MdwikiApi: Failed to fetch data from MDWiki REST API for title: %s", title)
            # Fallback to Action API
            if self.fallback_to_action_api:
                return self._fetch_action_api(title)

            return "", "", error or "Empty response"

        try:
            data = json.loads(output)
            source = data.get("source", "")
            revid = data.get("latest", {}).get("id", "")
            return source, str(revid), ""

        except Exception as exc:
            logger.error("Failed to parse MDWiki REST response: %s", exc)
            if self.fallback_to_action_api:
                return self._fetch_action_api(title)

            return "", "", error or "Empty response"

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

        output = response.get("output")
        error = response.get("error")

        if response["error"] or not output:
            logger.error("MdwikiApi: Failed to fetch data from MDWiki API for title: %s", title)
            return "", "", response.get("error") or "Empty response"

        try:
            data = json.loads(output)
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

        if not source:
            logger.error("WikitextHandler: wikitext empty for title: %s", title)

        return source, str(revid) if revid else "", error

class TransformApi:
    """Convert wikitext to HTML using English Wikipedia REST API."""

    def convert(self, wikitext: str, title: str) -> dict[str, str]:
        """
        Returns {"result": html} or {"error": message}.
        """
        if not wikitext:
            return {"error": "Empty wikitext"}

        base_url = settings.new_html.transform_base_url

        title_encoded = normalize_title_for_url(title)
        url = f"{base_url}/transform/wikitext/to/html/{title_encoded}"

        response = _request(
            url,
            method="POST",
            data={"wikitext": wikitext},
            timeout=30.0,
        )

        response_output = response.get("output")
        error = response.get("error")
        error_code = response.get("error_code")

        # Handle the response from the API
        if response_output:
            logger.error("TransformApi: API request failed for title: %s", title)
            if error:
                logger.error("Error details: %s (%s)", error, error_code)

            return {"error": response.get("error") or "Error: Could not reach API."}

        html = response_output or ""

        # Check if response contains an error
        if ">Wikimedia Error" in html:
            logger.error("TransformApi: API returned error for title: %s", title)
            return {"error": "Error: Wikipedia API returned an error."}

        # Check if response is valid HTML
        if "<html" not in html.lower():
            logger.error("TransformApi: API returned invalid HTML for title: $title");
            return {"error": "Error: Wikipedia API returned invalid HTML."}

        return {"result": html}


__all__ = [
    "MdwikiApi",
    "TransformApi",
    "normalize_title_for_url",
]
