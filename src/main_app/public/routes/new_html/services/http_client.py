"""
HTTP client service for making external API requests.
"""

import logging
from typing import Any

import httpx

from app.new_html.config import USER_AGENT

logger = logging.getLogger(__name__)


class HttpClient:
    """
    Simple HTTP client wrapper around httpx.
    """

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": USER_AGENT,
        }

    def request(
        self,
        url: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Send an HTTP request and return a normalized response.

        Returns:
            {
                "output": str,
                "error_code": str,
                "error": str,
                "http_code": int,
            }
        """
        result = {
            "output": "",
            "error_code": "",
            "error": "",
            "http_code": 0,
        }

        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
                response = client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    data=data,
                    json=json,
                )

                result["http_code"] = response.status_code

                if response.status_code != 200:
                    result["error_code"] = str(response.status_code)
                    result["error"] = "HTTP_ERROR"
                    logger.warning(f"HTTP {response.status_code} for URL: {url}")
                    return result

                result["output"] = response.text

        except httpx.TimeoutException:
            result["error_code"] = "TIMEOUT"
            result["error"] = "Request timed out"
            logger.error(f"Timeout while requesting: {url}")
        except Exception as e:
            result["error_code"] = "REQUEST_ERROR"
            result["error"] = str(e)
            logger.error(f"Request failed for {url}: {e}")

        return result
