"""Configuration and fixtures for pytest"""

import os
import sys
from pathlib import Path

import pytest

# Set environment variables before any imports that might need them
os.environ.setdefault("FLASK_SECRET_KEY", "test_secret_key_12345678901234567890")
os.environ.setdefault("OAUTH_MWURI", "https://en.wikipedia.org/w/index.php")
os.environ.setdefault("OAUTH_CONSUMER_KEY", "test")
os.environ.setdefault("OAUTH_CONSUMER_SECRET", "test")

# Use a fixed encryption key for test reproducibility
# This is a valid Fernet key for testing only - DO NOT use in production
TEST_ENCRYPTION_KEY = "rSsfrKOh-Tu_hcyJBdVwNxna9QtI1v5kuftpX6-bRXI="
os.environ.setdefault("OAUTH_ENCRYPTION_KEY", TEST_ENCRYPTION_KEY)

# Get the project root directory (parent of pytests folder)
project_root = Path(__file__).parent.parent

# Add python_src to sys.path so we can import from 'src' as a package
python_src_path = project_root  # / "python_src"
sys.path.insert(0, str(python_src_path))


# Import after environment setup
from src.app_main import create_app  # noqa: E402
from src.app_main.config import TestingConfig  # noqa: E402


@pytest.fixture
def app():
    """Create and configure a test Flask application.

    Yields:
        Flask application configured for testing.
    """
    app = create_app(TestingConfig)

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create a test client for the app.

    Args:
        app: The Flask application fixture.

    Returns:
        Test client for making HTTP requests.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the app.

    Args:
        app: The Flask application fixture.

    Returns:
        Test CLI runner for invoking commands.
    """
    return app.test_cli_runner()


@pytest.fixture
def auth_client(app):
    """Create an authenticated test client.

    This fixture provides a test client with a logged-in user session.
    Useful for testing protected routes.

    Args:
        app: The Flask application fixture.

    Returns:
        Authenticated test client.
    """
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["uid"] = 12345
        sess["username"] = "TestUser"

    return client
