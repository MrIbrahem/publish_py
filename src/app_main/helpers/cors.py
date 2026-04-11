"""CORS validation helpers.

Mirrors: php_src/bots/cors.php
"""

import logging
from flask import current_app, request

from ..config import settings

logger = logging.getLogger(__name__)


def is_allowed() -> str | None:
    """Check if request is from allowed domain.

    Returns the allowed domain name or None.
    """
    if current_app.config.CORS_DISABLED:
        return "test"

    if not settings.cors.allowed_domains:
        return None

    referer = request.headers.get("Referer", "")
    origin = request.headers.get("Origin", "")

    for domain in settings.cors.allowed_domains:
        if domain in referer or domain in origin:
            return domain
    logger.warning(f"Access denied: referer={referer}, origin={origin}")
    return None
