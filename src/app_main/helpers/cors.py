"""CORS validation helpers.

Mirrors: php_src/bots/cors.php
"""

from flask import request

from ..config import settings


def is_allowed() -> str | None:
    """Check if request is from allowed domain.

    Returns the allowed domain name or None.
    """
    referer = request.headers.get("Referer", "")
    origin = request.headers.get("Origin", "")

    for domain in settings.cors.allowed_domains:
        if domain in referer or domain in origin:
            return domain
    return None
