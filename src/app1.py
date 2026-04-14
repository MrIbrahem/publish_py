"""
WSGI entry point for the Flask application.
"""

from __future__ import annotations
import os
import logging
from pathlib import Path

# Load environment variables before any other imports
from env_config import load_environment

load_environment()

from app_main import create_app  # noqa: E402
from app_main.config import DevelopmentConfig  # noqa: E402
from logger_config import configure_logging

configure_logging(logging.DEBUG)

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run(debug=True)
