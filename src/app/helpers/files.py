"""File logging utilities.

Mirrors: php_src/bots/files_helps.php
"""

import json
import logging
import os
import uuid
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..config import settings

logger = logging.getLogger(__name__)

# Generate a random ID for this process/session
# This mirrors the PHP $RAND_ID behavior
_RAND_ID: str | None = None


def _get_rand_id() -> str:
    """Get a random session ID.

    Returns a short unique ID for this process session.
    The ID is generated once per process and reused.
    """
    global _RAND_ID
    if _RAND_ID is None:
        _RAND_ID = uuid.uuid4().hex[:8]
    return _RAND_ID


def get_reports_dir() -> Path:
    """Get/create the reports directory structure.

    Returns the path to the reports directory for today:
    {main_dir}/publish_reports/reports_by_day/YYYY/MM/DD/{rand_id}/
    """
    main_dir = os.getenv("MAIN_DIR", os.path.expanduser("~/data"))
    publish_reports = Path(main_dir) / "publish_reports" / "reports_by_day"

    # Create directory structure: YYYY/MM/DD/rand_id
    now = datetime.now()
    day_dir = publish_reports / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}" / _get_rand_id()
    day_dir.mkdir(parents=True, exist_ok=True)

    return day_dir


def to_do(tab: dict[str, Any], status: str) -> None:
    """Log operation to file and save to reports_by_day directory.

    Args:
        tab: Operation data dictionary
        status: Status string (e.g., "noaccess", "success", "error")

    This function writes to two locations:
    1. JSON lines log file in log_dir (for backwards compatibility)
    2. Individual JSON file in reports_by_day/YYYY/MM/DD/{rand_id}/ (PHP-style)
    """
    now = datetime.now()

    # Add timestamp and status to the entry
    log_entry = {
        "time": int(now.timestamp()),
        "time_date": now.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        **tab,
    }

    # Write to JSON lines log file (existing behavior)
    log_dir = Path(settings.paths.log_dir)
    today = now.strftime("%Y-%m-%d")
    log_file = log_dir / f"publish_{today}.json"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to write to log file {log_file}: {e}")

    # Write to reports_by_day directory (PHP-style file-based reports)
    try:
        reports_dir = get_reports_dir()
        file_path = reports_dir / f"{status}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to write to reports file {file_path}: {e}")
