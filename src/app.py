"""
WSGI entry point for the Flask application.
"""

from __future__ import annotations
from app_main import create_app
from app_main.config import ProductionConfig
from log import config_console_logger

config_console_logger()

app = create_app(ProductionConfig)

if __name__ == "__main__":
    app.run()
