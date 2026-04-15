"""
# isort:skip_file
WSGI entry point for the Flask application for Production
"""

from __future__ import annotations
import logging

# Load environment variables before any other imports
from env_config import load_environment  # auto-load load_environment()

from new_app import create_app
from new_app.config import ProductionConfig
from logger_config import configure_logging

configure_logging(logging.INFO)

app = create_app(ProductionConfig)

if __name__ == "__main__":
    app.run()
