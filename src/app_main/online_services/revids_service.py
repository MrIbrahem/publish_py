"""Revision ID lookup service.

Mirrors: php_src/bots/revids_bot.php
"""

import json
import logging
from pathlib import Path

import requests

from ..config import settings

logger = logging.getLogger(__name__)


def get_revid(sourcetitle: str) -> str:
    """Get revision ID from local JSON file.

    Args:
        sourcetitle: Source page title

    Returns:
        Revision ID as string, or empty string if not found
    """
    revids_file_path: Path = settings.paths.revids_file_path

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


def get_revid_db(sourcetitle: str) -> str:
    """Get revision ID from database API.

    Args:
        sourcetitle: Source page title

    Returns:
        Revision ID as string, or empty string if not found
    """
    params = {
        "get": "revids",
        "title": sourcetitle,
    }

    if not settings.revids_api_url:
        logger.warning("revids_api_url not set in config")
        return ""

    headers = {"User-Agent": settings.user_agent}
    try:
        response = requests.get(settings.revids_api_url, headers=headers, params=params, timeout=30)
        data = response.json()
        results = {r["title"]: str(r["revid"]) for r in data.get("results", [])}
        return results.get(sourcetitle, "")
    except Exception as e:
        logger.error(f"Error fetching revid from API: {e}")
        return ""
