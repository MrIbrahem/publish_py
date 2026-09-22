"""
# isort:skip_file
WSGI development entry point for the app.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
import pymysql

# Set environment mode
os.environ["FLASK_ENV"] = "development"

# Ensure current directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Register PyMySQL driver
pymysql.install_as_MySQLdb()

# Initialize environment variables and external module paths before application setup
from main_app.bootstrap import init_app_environment  # Adjust import based on module location  # noqa: E402

init_app_environment()

from main_app import AppFactory  # noqa: E402

app = AppFactory.create()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
