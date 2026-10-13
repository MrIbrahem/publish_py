"""
Utility helpers for the new_html module.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ....config.main_settings import get_settings

logger = logging.getLogger(__name__)


class FileUtils:

    @staticmethod
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

    @staticmethod
    def read_file(file_path: Path | str | None) -> str:
        """
        Read the contents of a file safely.

        Returns empty string on any error.
        """
        if not file_path:
            return ""

        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return ""

        try:
            return path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.error("Could not read file %s: %s", path, exc)
            return ""

    @staticmethod
    def write_file(file_path: Path | str | None, text: str) -> None:
        """
        Write text to a file.
        Creates parent directories if needed.
        """
        if not file_path or not text:
            return

        path = Path(file_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        except Exception as exc:
            logger.error("Could not write to file %s: %s", path, exc)


__all__ = [
    "FileUtils",
]
