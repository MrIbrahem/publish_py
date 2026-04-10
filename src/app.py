"""
WSGI entry point for the Flask application.
"""

from __future__ import annotations

import sys

# Load environment variables before any other imports
from env_config import load_environment
from .app_main.config import ProductionConfig

load_environment()

from app_main import create_app  # noqa: E402
from log import config_console_logger  # noqa: E402

config_console_logger()

app = create_app(ProductionConfig)

if __name__ == "__main__":
    debug = "debug" in sys.argv or "DEBUG" in sys.argv
    app.run(debug=debug)
