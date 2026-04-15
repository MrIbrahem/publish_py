"""
CORS validation helpers.

Mirrors: php_src/bots/cors.php

"""
import logging
from urllib.parse import urlparse
from flask import current_app
from flask.wrappers import Request

from ..config import settings

logger = logging.getLogger(__name__)


def get_host(url: str) -> str:
    return urlparse(url).netloc


def make_url(url) -> str:
    if not url or not isinstance(url, str):
        return None

    url_obj = urlparse(url)
    result = f"{url_obj.scheme}://{url_obj.netloc}"

    if not url_obj.scheme or not url_obj.netloc or result == "://":
        logger.warning(f"bad urlparse: {url=}")
        logger.warning(url_obj)
        return ""

    return result


def _get_allowed_domains() -> list[str]:
    return settings.cors.allowed_domains


def is_allowed(request: Request) -> str | None:
    """Check if request is from an exact allowed domain or same origin."""
    referer = request.headers.get("Referer", "")
    origin = request.headers.get("Origin", "")

    # Extract the host (netloc) from our current server URL
    # e.g., 'example.com' or 'localhost:5000'
    server_host = get_host(request.host_url)
    # server_host = request.host or get_host(request.host_url)

    # Helper function to extract host from a URL string

    origin_host = get_host(origin) if origin else ""

    if current_app.config.get("CORS_DISABLED"):
        logger.warning(f"CORS is disabled. Access allowed: referer={referer}, origin={origin}")
        # # return origin_host or "*"
        return make_url(origin) or "*"

    referer_host = get_host(referer) if referer else ""

    # 1. Check for Same-Origin (Exact Host Match)
    if (origin_host and origin_host == server_host) or (referer_host and referer_host == server_host):
        # # return origin_host or server_host
        return make_url(origin) or make_url(request.host_url)

    if not _get_allowed_domains():
        logger.warning(f"Access denied: referer={referer}, origin={origin}, no allowed_domains available")
        return None

    # 2. Check for Exact Match in allowed domains list
    # Assuming allowed_domains contains: ['mysite.com', 'api.mysite.com']
    for domain in _get_allowed_domains():
        if origin_host == domain:
            # # return domain
            return make_url(origin)

        if referer_host == domain:
            # # return domain
            return make_url(referer)

    # Access denied: referer_host='google.com', origin_host='google.com'
    logger.warning(f"Access denied: {referer_host=}, {origin_host=}")
    return None
