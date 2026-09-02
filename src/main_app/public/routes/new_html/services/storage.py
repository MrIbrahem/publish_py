"""
Filesystem cache and title → revision index management.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from .....config.main_settings import get_settings

logger = logging.getLogger(__name__)


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


def get_title_revision(title: str, all_flag: str = "") -> str:
    """
    Get the stored revision ID for a title from the JSON index.
    """
    settings = get_settings()
    json_path = settings.new_html.json_file_all if all_flag else settings.new_html.json_file

    content = read_file(json_path)
    if not content:
        return ""

    try:
        data = json.loads(content)
        return str(data.get(title, ""))
    except Exception:
        return ""


def add_title_revision(title: str, revision: str, all_flag: str = "") -> None:
    """
    Add or update a title → revision mapping in the JSON index.
    """
    if not title or not revision:
        return

    settings = get_settings()
    json_path = settings.new_html.json_file_all if all_flag else settings.new_html.json_file

    content = read_file(json_path)
    try:
        data = json.loads(content) if content else {}
    except Exception:
        data = {}

    data[title] = str(revision)
    write_file(json_path, json.dumps(data, ensure_ascii=False, indent=2))


def list_revisions() -> list[dict[str, Any]]:
    """
    Return a sorted list of cached revisions for the dashboard.

    Sorted by last modification time of wikitext.txt (newest first).
    """
    settings = get_settings()
    revisions_dir = settings.new_html.revisions_dir

    if not revisions_dir.exists():
        return []

    dirs = [d for d in revisions_dir.iterdir() if d.is_dir()]

    def sort_key(d: Path) -> float:
        wikitext = d / "wikitext.txt"
        if wikitext.exists():
            return wikitext.stat().st_mtime
        return d.stat().st_mtime

    dirs.sort(key=sort_key, reverse=True)

    results: list[dict[str, Any]] = []

    for idx, dir_path in enumerate(dirs, start=1):
        dir_name = dir_path.name
        oldid = dir_name.replace("_all", "")

        wikitext_file = dir_path / "wikitext.txt"
        if wikitext_file.exists():
            last_modified = datetime.fromtimestamp(wikitext_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        else:
            last_modified = datetime.fromtimestamp(dir_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")

        title_file = dir_path / "title.txt"
        title = read_file(title_file).replace("_", " ") if title_file.exists() else ""

        results.append(
            {
                "number": idx,
                "lastModified": last_modified,
                "title": title,
                "dir_path": dir_name,
                "oldid_number": oldid,
                "wikitext_exists": (dir_path / "wikitext.txt").exists(),
                "html_exists": (dir_path / "html.html").exists(),
                "seg_exists": (dir_path / "seg.html").exists(),
            }
        )

    return results
