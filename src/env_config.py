"""
Central configuration for the web application.

This module handles loading environment variables from .env files.
It should be imported and initialized at application startup.
"""

import logging

logger = logging.getLogger(__name__)


def load_environment() -> None:
    """Load environment variables from .env files.

    This function loads environment variables from .env files

    This function is safe to call multiple times - subsequent calls will not
    override already loaded environment variables.
    """
