"""File logging utilities.

Mirrors: php_src/bots/files_helps.php
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config import settings

logger = logging.getLogger(__name__)


def to_do(tab: dict[str, Any], status: str) -> None:
    """Log operation to file.

    Args:
        tab: Operation data dictionary
        status: Status string (e.g., "noaccess", "success", "error")
    """
    log_dir = Path(settings.paths.log_dir)
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"publish_{today}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        **tab,
    }

    try:
        # Append to JSON lines file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to write to log file {log_file}: {e}")
