"""CORS validation helpers.

Mirrors: php_src/bots/cors.php

"""
import logging
from urllib.parse import urlparse
from flask import current_app, request

from .config import settings

logger = logging.getLogger(__name__)


def check_publish_secret_code() -> str | None:
    expected_secret = settings.publish_secret_code
    if not expected_secret:
        return None

    received_secret = request.headers.get("X-Secret-Key")

    if received_secret and received_secret == expected_secret:
        origin = request.headers.get("Origin")
        if origin:
            return urlparse(origin).netloc
        return urlparse(request.host_url).netloc

    return None


def _is_allowed() -> str | None:
    """Check if request is from an exact allowed domain or same origin."""
    referer = request.headers.get("Referer", "")
    origin = request.headers.get("Origin", "")

    # Extract the host (netloc) from our current server URL
    # e.g., 'example.com' or 'localhost:5000'
    server_host = urlparse(request.host_url).netloc

    if current_app.config.get("CORS_DISABLED"):
        logger.warning(f"CORS is disabled. Access allowed: referer={referer}, origin={origin}")
        return origin or "*"

    # Helper function to extract host from a URL string
    def get_host(url: str) -> str:
        return urlparse(url).netloc

    origin_host = get_host(origin) if origin else ""
    referer_host = get_host(referer) if referer else ""

    # 1. Check for Same-Origin (Exact Host Match)
    if (origin_host and origin_host == server_host) or (referer_host and referer_host == server_host):
        return origin or request.host_url.rstrip('/')

    if not settings.cors.allowed_domains:
        logger.warning(f"Access denied: referer={referer}, origin={origin}")
        return None

    # 2. Check for Exact Match in allowed domains list
    # Assuming allowed_domains contains: ['mysite.com', 'api.mysite.com']
    for domain in settings.cors.allowed_domains:
        if (origin_host == domain) or (referer_host == domain):
            # return origin or f"https://{domain}"
            return domain

    logger.warning(f"Access denied: referer={referer}, origin={origin}")
    # Avoid logging sensitive headers like X-Secret-Key
    return None


def is_allowed() -> str | None:
    return check_publish_secret_code() or _is_allowed()
