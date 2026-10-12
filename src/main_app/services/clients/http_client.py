"""HTTP client service for unified web requests."""

from __future__ import annotations

import logging
from typing import Any

import requests

from ...config import app_settings

logger = logging.getLogger(__name__)


class HttpClient:
    """HTTP client wrapper providing standardized methods for HTTP requests.

    - ``get`` / ``post`` / ``request`` return a raw ``requests.Response``.
    - ``safe_request`` never raises and returns a result dict with
      ``output``, ``error``, ``error_code`` and ``http_code``.
    """

    def __init__(self, default_timeout: float = 30.0, user_agent: str | None = None) -> None:
        self.default_timeout = default_timeout
        self._user_agent = user_agent

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @property
    def user_agent(self) -> str:
        if self._user_agent is not None:
            return self._user_agent
        try:
            return app_settings.other.user_agent
        except Exception:
            return "MDWikiCX/1.0"

    def _prepare_headers(self, headers: dict[str, str] | None) -> dict[str, str]:
        req_headers = dict(headers) if headers is not None else {}
        if not any(key.lower() == "user-agent" for key in req_headers):
            req_headers["User-Agent"] = self.user_agent
        return req_headers

    def _send(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None,
        timeout: float | None,
        **kwargs: Any,
    ) -> requests.Response:
        """Single place where every request is actually sent."""
        return requests.request(
            method=method.upper(),
            url=url,
            headers=self._prepare_headers(headers),
            timeout=timeout if timeout is not None else self.default_timeout,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Raw-response API
    # ------------------------------------------------------------------
    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        auth: Any = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Perform an HTTP GET request."""
        req_headers = self._prepare_headers(headers)
        req_timeout = timeout if timeout is not None else self.default_timeout
        return requests.get(
            url,
            params=params,
            headers=req_headers,
            auth=auth,
            timeout=req_timeout,
            **kwargs,
        )

    def post(
        self,
        url: str,
        data: Any = None,
        json: Any = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        auth: Any = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Perform an HTTP POST request."""
        req_headers = self._prepare_headers(headers)
        req_timeout = timeout if timeout is not None else self.default_timeout
        return requests.post(
            url,
            data=data,
            json=json,
            params=params,
            headers=req_headers,
            auth=auth,
            timeout=req_timeout,
            **kwargs,
        )

    def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        auth: Any = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Perform a generic HTTP request."""
        req_headers = self._prepare_headers(headers)
        req_timeout = timeout if timeout is not None else self.default_timeout
        return requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json_data,
            headers=req_headers,
            auth=auth,
            timeout=req_timeout,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Safe (dict-result) API
    # ------------------------------------------------------------------
    def safe_request(
        self,
        url: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 15.0,
    ) -> dict[str, Any]:
        """Perform a request without raising; return a result dict.

        Keys: ``output`` (body on HTTP 200), ``error``, ``error_code``, ``http_code``.
        """
        result: dict[str, Any] = {
            "output": "",
            "error": "",
            "error_code": "",
            "http_code": 0,
        }

        try:
            response = self.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json_data=json_data,
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

        result["http_code"] = response.status_code

        if response.status_code != 200:
            logger.error("HttpClient: API returned HTTP %s for %s", response.status_code, url)
            result["error"] = "HTTP_ERROR"
            result["error_code"] = str(response.status_code)

            # check Cloudflare protection
            if "Just a moment..." in response.text:
                logger.error("Cloudflare protection detected for %s", url)
                result["error"] = "CLOUDFLARE_PROTECTION"
            else:
                logger.error(repr(response.text))

            return result

        result["output"] = response.text
        return result


http_client = HttpClient()

__all__ = [
    "HttpClient",
    "http_client",
]
