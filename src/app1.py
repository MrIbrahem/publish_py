"""
# isort:skip_file
WSGI entry point for the Flask application for Development
"""

from __future__ import annotations
import logging
import pymysql

pymysql.install_as_MySQLdb()

# Load environment variables before any other imports
from env_config import load_environment  # auto-load load_environment()
from sqlalchemy_app import create_app  # noqa: E402
from sqlalchemy_app.config import DevelopmentConfig  # noqa: E402

from logger_config import configure_logging

configure_logging(logging.DEBUG)

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run(debug=True)
