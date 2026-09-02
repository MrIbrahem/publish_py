"""
Helpers for managing title → revision_id JSON mappings.
"""

import json
from pathlib import Path

from ..services.file_utils import read_file, write_file


def get_title_revision(title: str, file_path: Path) -> str:
    """
    Get the stored revision ID for a title.
    """
    content = read_file(file_path)
    if not content:
        return ""

    try:
        data = json.loads(content)
        return str(data.get(title, ""))
    except Exception:
        return ""


def add_title_revision(title: str, revision: str, file_path: Path) -> None:
    """
    Add or update a title → revision mapping.
    """
    if not title or not revision:
        return

    content = read_file(file_path)
    try:
        data = json.loads(content) if content else {}
    except Exception:
        data = {}

    data[title] = revision
    write_file(file_path, json.dumps(data, ensure_ascii=False, indent=2))


__all__ = [
    "get_title_revision",
    "add_title_revision",
]
