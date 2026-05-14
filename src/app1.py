"""
# isort:skip_file
WSGI development entry point for the app.
"""

from __future__ import annotations
import sys
import logging
import pymysql
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
pymysql.install_as_MySQLdb()

# Load environment variables before any other imports

try:
    load_dotenv()
except Exception:
    logging.warning("Failed to load .env file from current working directory")

# import app here
from sqlalchemy_app import create_app  # noqa: E402
from sqlalchemy_app.config import DevelopmentConfig  # noqa: E402

from logger_config import configure_logging  # noqa: E402

configure_logging(logging.DEBUG)

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run(debug=True)
