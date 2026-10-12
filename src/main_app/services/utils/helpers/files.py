"""File logging utilities.

Mirrors: php_src/bots/files_helps.php

Structure:
    SessionIdProvider : short random ID, generated once per process
    ReportsDirectory  : builds/creates the daily reports directory
    ToDoLogger        : writes an operation to the JSON-lines log and to a report file

Public entry points: `to_do`.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from ....config import app_settings

logger = logging.getLogger(__name__)


class SessionIdProvider:
    """Short unique ID for this process/session (mirrors PHP $RAND_ID).

    The ID is generated once per process and reused.
    """

    _rand_id: str | None = None

    @classmethod
    def get(cls) -> str:
        if cls._rand_id is None:
            cls._rand_id = uuid.uuid4().hex[:8]
        return cls._rand_id


class ReportsDirectory:
    """Daily reports directory: {publish_reports_dir}/YYYY/MM/DD/{rand_id}/"""

    @staticmethod
    def get(now: datetime | None = None) -> Path:
        """Get/create the reports directory for the given moment (default: now)."""
        now = now or datetime.now()
        publish_reports: Path = app_settings.paths.publish_reports_dir

        # Create directory structure: YYYY/MM/DD/rand_id
        day_dir = publish_reports / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}" / SessionIdProvider.get()
        day_dir.mkdir(parents=True, exist_ok=True)

        return day_dir


class ToDoLogger:
    """Logs an operation to two locations:

    1. JSON lines log file in flask_data_dir/publishes
    2. Individual JSON file in reports_by_day/YYYY/MM/DD/{rand_id}/ (PHP-style)
    """

    @staticmethod
    def build_entry(tab: dict[str, Any], status: str, now: datetime) -> dict[str, Any]:
        """Copy tab, then add time/status keys."""
        log_entry = dict(tab)
        log_entry["time"] = int(now.timestamp())
        log_entry["time_date"] = now.strftime("%Y-%m-%d %H:%M:%S")
        log_entry["status"] = status
        return log_entry

    @staticmethod
    def _write_log_line(log_entry: dict[str, Any], now: datetime) -> None:
        """Append the entry to the daily JSON lines file."""
        flask_data_dir: Path = app_settings.paths.flask_data_dir
        today = now.strftime("%Y-%m-%d")
        log_file = flask_data_dir / "publishes" / f"publish_{today}.json"

        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write to log file {log_file}: {e}")

    @staticmethod
    def _write_report_file(log_entry: dict[str, Any], status: str, now: datetime) -> None:
        """Write the entry as an individual JSON file (PHP-style report)."""
        try:
            reports_dir = ReportsDirectory.get(now)
        except Exception as e:
            logger.error(f"Failed to write to reports file {status}.json: {e}")
            return

        file_path = reports_dir / f"{status}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(log_entry, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to write to reports file {status}.json: {e}")

    def log(self, tab: dict[str, Any], status: str) -> None:
        """Log the operation.

        Args:
            tab: Operation data dictionary
            status: Status string (e.g., "noaccess", "success", "error")
        """
        now = datetime.now()
        log_entry = self.build_entry(tab, status, now)

        self._write_log_line(log_entry, now)
        self._write_report_file(log_entry, status, now)


__all__ = [
    "SessionIdProvider",
    "ReportsDirectory",
    "ToDoLogger",
]
