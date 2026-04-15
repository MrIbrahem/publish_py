"""
Central configuration for the web application.

This module handles loading environment variables from .env files.
It should be imported and initialized at application startup.
"""

import logging

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_environment() -> None:
    """Load environment variables from .env files.

    This function loads environment variables from .env files

    This function is safe to call multiple times - subsequent calls will not
    override already loaded environment variables.
    """
    try:
        load_dotenv()
    except Exception:
        logger.warning("Failed to load .env file from current working directory")


# Keep backward compatibility: auto-load on import for legacy code
# New code should call load_environment() explicitly
load_environment()
