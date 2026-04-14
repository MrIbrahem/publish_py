"""CORS validation helpers.

Mirrors: php_src/bots/cors.php

"""
import logging
from urllib.parse import urlparse
from flask import Request, current_app

from ..config import settings

logger = logging.getLogger(__name__)


def is_allowed(request: Request) -> str | None:
    """Check if request is from an exact allowed domain or same origin."""
    referer = request.headers.get("Referer", "")
    origin = request.headers.get("Origin", "")

    # Extract the host (netloc) from our current server URL
    # e.g., 'example.com' or 'localhost:5000'
    server_host = urlparse(request.host_url).netloc

    # Helper function to extract host from a URL string
    def get_host(url: str) -> str:
        return urlparse(url).netloc

    if current_app.config.get("CORS_DISABLED"):
        logger.warning(f"CORS is disabled. Access allowed: referer={referer}, origin={origin}")
        return origin or "*"

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
    return None
