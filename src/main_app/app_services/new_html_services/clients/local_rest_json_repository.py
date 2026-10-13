import json
import logging
import os
from pathlib import Path
from typing import Any

from .mdwiki_api import normalize_title_for_url


class LocalRestJsonRepository:
    """Reads cached MDWiki REST responses from the local data directory."""

    def __init__(self, base_dir: str | None = None) -> None:
        """Initialize the repository.

        :param base_dir: Optional base directory path for cached files
        """
        self.base_dir = base_dir if base_dir is not None else self._default_dir()

    @staticmethod
    def title_to_file_name(title: str) -> str:
        """Convert a page title to a corresponding JSON file name."""
        return f"{normalize_title_for_url(title)}.json"

    @staticmethod
    def _default_dir() -> str:
        """Get the default directory path based on the user's home directory."""
        home = os.getenv("HOME", "")

        return f"{home.rstrip('/')}/data/rtt_members"

    def find(self, title: str) -> dict[str, Any] | None:
        """Find and read cached JSON data for a given title safely.

        :param title: The page title to look up
        :return: Dictionary containing the JSON data, or None if not found/invalid
        """
        base_path = Path(self.base_dir).resolve()
        if not base_path.is_dir():
            return None

        file_path = (base_path / self.title_to_file_name(title)).resolve()

        # Ensure the file is within the base directory to prevent path traversal
        try:
            file_path.relative_to(base_path)
        except ValueError:
            return None

        if not file_path.is_file():
            return None

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return None

        try:
            json_data = json.loads(content)
        except json.JSONDecodeError:
            logging.error(f"LocalRestJsonRepository: invalid json in local file for title: {title}")
            return None

        if not isinstance(json_data, dict):
            logging.error(f"LocalRestJsonRepository: invalid json in local file for title: {title}")
            return None

        return json_data
