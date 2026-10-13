"""
- TransformApiService: wikitext → HTML
"""

from __future__ import annotations

import logging

from ....config.main_settings import app_settings
from ....services.clients.http_client import HttpClient

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


class TransformApiService:
    """Convert wikitext to HTML using English Wikipedia REST API."""

    def __init__(
        self,
        http_client: HttpClient | None = None,
    ) -> None:
        """Initialize the checker with an HTTP client instance."""
        self.http_client = http_client or HttpClient()

    def convert(self, wikitext: str, title: str) -> dict[str, str]:
        """
        Returns {"result": html} or {"error": message}.
        """
        if not wikitext:
            return {"error": "Empty wikitext"}

        base_url = app_settings.new_html.transform_base_url

        title_encoded = normalize_title_for_url(title)
        url = f"{base_url}/transform/wikitext/to/html/{title_encoded}"

        response = self.http_client.safe_request(
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
            logger.error("API request failed for title: %s", title)
            if error:
                logger.error("Error details: %s (%s)", error, error_code)

            return {"error": response.get("error") or "Error: Could not reach API."}

        html = response_output or ""

        # Check if response contains an error
        if ">Wikimedia Error" in html:
            logger.error("API returned error for title: %s", title)
            return {"error": "Error: Wikipedia API returned an error."}

        # Check if response is valid HTML
        if "<html" not in html.lower():
            logger.error("API returned invalid HTML for title: $title")
            return {"error": "Error: Wikipedia API returned invalid HTML."}

        return {"result": html}


__all__ = [
    "TransformApiService",
]
