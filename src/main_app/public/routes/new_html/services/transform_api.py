"""
Service for converting wikitext to HTML using Wikipedia REST API.
"""

import logging

from .http_client import HttpClient

logger = logging.getLogger(__name__)


class TransformApiService:
    """
    Converts wikitext to HTML via Wikipedia's transform endpoint.
    """

    def __init__(self, http_client: HttpClient | None = None):
        self.http = http_client or HttpClient()
        self.base_url = "https://en.wikipedia.org/w/rest.php/v1"

    def convert(self, wikitext: str, title: str) -> dict[str, str]:
        """
        Convert wikitext to HTML.

        Returns:
            {"result": str} on success or {"error": str} on failure.
        """
        if not wikitext:
            return {"error": "Empty wikitext"}

        title_encoded = title.replace("/", "%2F")
        url = f"{self.base_url}/transform/wikitext/to/html/{title_encoded}"

        response = self.http.request(
            url,
            method="POST",
            data={"wikitext": wikitext},
        )

        if response["error"] or not response["output"]:
            logger.error(f"Transform API failed for title: {title}")
            return {"error": response.get("error") or "Empty response"}

        html = response["output"]

        # Basic validation
        if "Wikimedia Error" in html:
            return {"error": "Wikipedia API returned an error"}

        if "<html" not in html.lower():
            return {"error": "Invalid HTML returned"}

        return {"result": html}


__all__ = [
    "TransformApiService",
]
