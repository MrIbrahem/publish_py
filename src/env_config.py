"""
Central configuration for the SVG Translate web application.

This module handles loading environment variables from .env files.
It should be imported and initialized at application startup.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_environment() -> None:
    """Load environment variables from .env files.

    This function loads environment variables from .env files in the following order:
    1. Default .env file in current working directory
    2. $HOME/.env if the first fails
    3. $HOME/confs/.env as a fallback

    This function is safe to call multiple times - subsequent calls will not
    override already loaded environment variables.
    """
    try:
        load_dotenv()
    except Exception:
        _HOME = os.getenv("HOME")

        if _HOME:
            env_path = Path(f"{_HOME}/.env")

            if not env_path.exists():
                env_path = Path(f"{_HOME}/confs/.env")

            load_dotenv(env_path)


def get_env_file_path() -> Path | None:
    """Get the path to the loaded .env file if found.

    Returns:
        Path to the .env file if found, None otherwise.
    """
    _HOME = os.getenv("HOME")
    if not _HOME:
        return None

    for path in [Path(".env"), Path(f"{_HOME}/.env"), Path(f"{_HOME}/confs/.env")]:
        if path.exists():
            return path

    return None


# Keep backward compatibility: auto-load on import for legacy code
# New code should call load_environment() explicitly
load_environment()
