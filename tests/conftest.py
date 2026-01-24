"""Configuration and fixtures for pytest"""

import os
import sys
from pathlib import Path

# Set environment variables before any imports that might need them
os.environ.setdefault("FLASK_SECRET_KEY", "test_secret_key_12345678901234567890")
os.environ.setdefault("OAUTH_MWURI", "https://en.wikipedia.org/w/index.php")
os.environ.setdefault("OAUTH_CONSUMER_KEY", "test")
os.environ.setdefault("OAUTH_CONSUMER_SECRET", "test")

# Generate encryption key if not set
from cryptography.fernet import Fernet

if not os.environ.get("OAUTH_ENCRYPTION_KEY"):
    os.environ["OAUTH_ENCRYPTION_KEY"] = Fernet.generate_key().decode()

# Get the project root directory (parent of pytests folder)
project_root = Path(__file__).parent.parent

# Add python_src to sys.path so we can import from 'src' as a package
python_src_path = project_root  # / "python_src"
sys.path.insert(0, str(python_src_path))
