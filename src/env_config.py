"""
Central configuration for the SVG Translate web application.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_HOME = os.getenv("HOME")
_env_file_path = f"{_HOME}/.env"

if _HOME is None or _HOME == "":
    _env_file_path = str(Path(__file__).parent / ".env")

load_dotenv(_env_file_path)
