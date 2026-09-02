"""
File system utilities for reading and writing cache files.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def read_file(file_path: str | Path | None) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file.

    Returns:
        File contents as string, or empty string on error.
    """
    if not file_path:
        return ""

    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return ""

    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Could not read file: {path} - {e}")
        return ""


def write_file(file_path: str | Path | None, text: str) -> None:
    """
    Write text to a file with exclusive locking behavior.

    Args:
        file_path: Path to the file.
        text: Content to write.
    """
    if not file_path or not text:
        return

    path = Path(file_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except Exception as e:
        logger.error(f"Could not write to file: {path} - {e}")
