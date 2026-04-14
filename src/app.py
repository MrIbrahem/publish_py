"""
WSGI entry point for the Flask application.
"""

from __future__ import annotations
import logging

from app_main import create_app
from app_main.config import ProductionConfig
from logger_config import configure_logging

configure_logging(logging.INFO)

app = create_app(ProductionConfig)

if __name__ == "__main__":
    app.run()
