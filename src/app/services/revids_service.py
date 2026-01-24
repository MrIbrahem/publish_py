"""Revision ID lookup service.

Mirrors: php_src/bots/revids_bot.php
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)


def get_revid(sourcetitle: str) -> str:
    """Get revision ID from local JSON file.

    Args:
        sourcetitle: Source page title

    Returns:
        Revision ID as string, or empty string if not found
    """
    # Try multiple locations for the revids file
    possible_paths = [
        Path(__file__).parent.parent.parent / "bots" / "all_pages_revids.json",
        Path(__file__).parent.parent.parent.parent / "php_src" / "bots" / "all_pages_revids.json",
    ]

    for revids_file in possible_paths:
        if revids_file.exists():
            try:
                with open(revids_file, encoding="utf-8") as f:
                    revids = json.load(f)
                return str(revids.get(sourcetitle, ""))
            except Exception as e:
                logger.error(f"Error reading revids file {revids_file}: {e}")

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

    # Determine if localhost
    is_local = os.getenv("FLASK_ENV") == "development"

    if is_local:
        url = "http://localhost:9001/api"
    else:
        url = "https://mdwiki.toolforge.org/api.php"

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        results = {r["title"]: str(r["revid"]) for r in data.get("results", [])}
        return results.get(sourcetitle, "")
    except Exception as e:
        logger.error(f"Error fetching revid from API: {e}")
        return ""
