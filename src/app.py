"""
# isort:skip_file
WSGI entry point for the Flask application.
"""

from __future__ import annotations

import sys
import env_config # type: ignore # Triggers environment configuration

from app_main import create_app  # noqa: E402
from log import config_console_logger  # noqa: E402

config_console_logger()

app = create_app()

if __name__ == "__main__":
    debug = "debug" in sys.argv or "DEBUG" in sys.argv
    app.run(debug=debug)
