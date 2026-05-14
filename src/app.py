"""
# isort:skip_file
WSGI production entry point for the app.
"""

from __future__ import annotations
import logging
import pymysql

pymysql.install_as_MySQLdb()

# Load environment variables before any other imports
from env_config import load_environment  # noqa: E402, F401

from sqlalchemy_app import create_app  # noqa: E402
from sqlalchemy_app.config import DevelopmentConfig  # noqa: E402
from logger_config import configure_logging  # noqa: E402

configure_logging(logging.WARNING)

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run(debug=False, port=5000)
