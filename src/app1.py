"""
WSGI entry point for the Flask application.
"""

from __future__ import annotations

# Load environment variables before any other imports
from env_config import load_environment

load_environment()

from app_main import create_app  # noqa: E402
from app_main.config import TestingConfig  # noqa: E402
from log import config_console_logger  # noqa: E402

config_console_logger()

app = create_app(TestingConfig)

if __name__ == "__main__":
    app.run(debug=True)
