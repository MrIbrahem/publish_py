"""
Utility helpers for the new_html module.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from flask import Request, Response

from .....config.main_settings import get_settings


def get_file_dir(revision: str, all_flag: str = "") -> Path:
    """
    Build the cache directory path for a given revision.

    Args:
        revision: Revision ID (must be numeric).
        all_flag: If non-empty, appends "_all" to the directory name.

    Returns:
        Path object of the revision directory.
    """
    if not revision or not str(revision).isdigit():
        return Path("")

    settings = get_settings()
    dir_name = f"{revision}_all" if all_flag else str(revision)
    file_dir = settings.new_html.revisions_dir / dir_name
    file_dir.mkdir(parents=True, exist_ok=True)
    return file_dir


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


def apply_cors_headers(response: Response, request: Request) -> Response:
    """
    Apply CORS headers if the request origin is allowed.
    Reuses the project's allowed domains when possible.
    """
    origin = request.headers.get("Origin", "")
    if not origin:
        return response

    try:
        origin_host = urlparse(origin).hostname or ""
    except Exception:
        return response

    settings = get_settings()

    # Prefer project-level CORS settings if available
    allowed_domains = getattr(settings.cors, "allowed_domains", None)
    if allowed_domains is None:
        # Fallback to the domains used by the original PHP tool
        allowed_domains = [
            "mdwikicx.toolforge.org",
            "mdwiki.toolforge.org",
            "medwiki.toolforge.org",
        ]

    if origin_host in allowed_domains:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"

    return response
