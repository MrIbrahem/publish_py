"""CORS validation helpers.

Mirrors: php_src/bots/cors.php
"""

import logging
from urllib.parse import urlparse
from flask import current_app, request

from ..config import settings

logger = logging.getLogger(__name__)


def is_allowed() -> str | None:
    """Check if request is from an allowed domain or the same origin.

    Returns the allowed domain name or None.
    """
    referer = request.headers.get("Referer", "")
    origin = request.headers.get("Origin", "")

    # 1. Get the current server's base URL (Same-Origin)
    host_url = request.host_url.rstrip('/')

    if current_app.config.get("CORS_DISABLED"):
        logger.warning(f"CORS is disabled. Access allowed: referer={referer}, origin={origin}")
        return origin or "*"

    # 2. Automatically allow requests from the same origin
    # Verify if Origin or Referer starts with our host URL
    if (origin and origin.startswith(host_url)) or (referer and referer.startswith(host_url)):
        return origin or host_url

    if not settings.cors.allowed_domains:
        logger.warning(f"Access denied: referer={referer}, origin={origin}")
        logger.warning("No allowed domains configured")
        return None

    # 3. Validate against allowed domains in settings
    for domain in settings.cors.allowed_domains:
        # Note: Using 'in' can be risky; using exact domain matching is safer
        if (origin and domain in origin) or (referer and domain in referer):
            return origin or domain

    logger.warning(f"Access denied: referer={referer}, origin={origin}")
    return None
