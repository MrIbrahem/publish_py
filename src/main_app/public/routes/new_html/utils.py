"""
Utility helpers for the new_html module.
"""

import logging
from pathlib import Path

from flask import Response, request

from .config import ALLOWED_ORIGINS, REVISIONS_PATH

logger = logging.getLogger(__name__)


def get_file_dir(revision: str, all_flag: str = "") -> Path:
    """
    Build the cache directory path for a given revision.

    Args:
        revision: Revision ID (must be numeric).
        all_flag: If non-empty, appends "_all" to the directory name.

    Returns:
        Path object of the revision directory.
    """
    if not revision or not revision.isdigit():
        logger.error("Invalid or empty revision in get_file_dir()")
        return Path("")

    dir_name = f"{revision}_all" if all_flag else revision
    file_dir = REVISIONS_PATH / dir_name

    file_dir.mkdir(parents=True, exist_ok=True)
    return file_dir


def set_cors_headers(response: Response) -> Response:
    """
    Apply CORS headers if the request origin is allowed.
    """
    origin = request.headers.get("Origin", "")
    if not origin:
        return response

    from urllib.parse import urlparse

    origin_host = urlparse(origin).hostname

    if origin_host in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"

    return response


def get_content_type(printetxt: str) -> str:
    """
    Return the appropriate Content-Type based on the printetxt parameter.
    """
    mapping = {
        "wikitext": "text/plain",
        "html": "text/html",
        "seg": "text/html",
    }
    return mapping.get(printetxt, "application/json")


__all__ = [
    "get_file_dir",
    "set_cors_headers",
    "get_content_type",
]
