"""
Utility helpers for the new_html module.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ...config.main_settings import get_settings

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
    if not revision or not str(revision).isdigit():
        logger.error("Invalid or empty revision in get_file_dir")
        return Path("")

    dir_name = f"{revision}_all" if all_flag else str(revision)
    settings = get_settings()
    file_dir = settings.new_html.revisions_dir / dir_name

    if not file_dir.exists():
        try:
            file_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory {file_dir}: {e}")

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


__all__ = [
    "get_file_dir",
    "get_content_type",
]
