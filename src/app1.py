"""
WSGI entry point for the Flask application.
"""

from __future__ import annotations
import logging

# Load environment variables before any other imports
from env_config import load_environment

load_environment()

from app_main import create_app  # noqa: E402
from app_main.config import DevelopmentConfig  # noqa: E402
from log import config_console_logger  # noqa: E402

config_console_logger(logging.DEBUG)

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run(debug=True)
