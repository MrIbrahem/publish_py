"""
Central configuration for the SVG Translate web application.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
_env_file_path = str(Path(__file__).parent / ".env")
_HOME = os.getenv("HOME")

if _HOME and not _env_file_path.exists():
    _env_file_path = Path(f"{_HOME}/.env")

    if not _env_file_path.exists():
        _env_file_path = Path(f"{_HOME}/confs/.env")

load_dotenv(_env_file_path)
