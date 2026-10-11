"""Revision ID lookup service.

Mirrors: php_src/bots/revids_bot.php

TODO: This file need to be deleted, insted use database table "mdwiki_revids" and mdwiki_revid_service.py
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import requests

from ...config import app_settings

logger = logging.getLogger(__name__)


def get_revid(sourcetitle: str) -> str:
    """Get revision ID from local JSON file.

    Args:
        sourcetitle: Source page title

    Returns:
        Revision ID as string, or empty string if not found
    """
    revids_file_path: Path = app_settings.paths.revids_file_path

    if not revids_file_path:
        logger.warning("revids_file_path not set in config")
        return ""

    if revids_file_path.exists():
        try:
            with open(revids_file_path, encoding="utf-8") as f:
                revids = json.load(f)
            return str(revids.get(sourcetitle, ""))
        except Exception as e:
            logger.error(f"Error reading revids file {revids_file_path}: {e}")

    return ""

__all__ = [
    "get_revid",
]
