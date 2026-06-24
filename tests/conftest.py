"""Configuration and fixtures for pytest"""

import logging
import os
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest
from flask.app import Flask
from flask.testing import FlaskClient
from sqlalchemy.exc import SQLAlchemyError

if sys:
    os.environ.setdefault("REVIDS_API_URL", "https://mdwiki.toolforge.org/api.php")
    os.environ.setdefault("SPECIAL_USERS", "Mr. Ibrahem 1:Mr. Ibrahem,Admin:Mr. Ibrahem")
    os.environ.setdefault("FALLBACK_USER", "Mr. Ibrahem")
    os.environ.setdefault("USERS_WITHOUT_HASHTAG", "Mr. Ibrahem")

    # Set environment variables before any imports that might need them
    os.environ.setdefault("FLASK_SECRET_KEY", "test_secret_key_12345678901234567890")
    os.environ.setdefault("OAUTH_MWURI", "https://en.wikipedia.org/w/index.php")
    os.environ.setdefault("OAUTH_CONSUMER_KEY", "test")
    os.environ.setdefault("OAUTH_CONSUMER_SECRET", "test")

    # Use a fixed encryption key for test reproducibility
    # This is a valid Fernet key for testing only - DO NOT use in production
    TEST_ENCRYPTION_KEY = "rSsfrKOh-Tu_hcyJBdVwNxna9QtI1v5kuftpX6-bRXI="
    os.environ.setdefault("OAUTH_ENCRYPTION_KEY", TEST_ENCRYPTION_KEY)

    os.environ.setdefault("WIKIDATA_DOMAIN", "test.wikidata.org")

    os.environ.setdefault("FLASK_DATA_DIR", "/tmp")
    os.environ.setdefault("PUBLISH_REPORTS_DIR", "/tmp/publish_reports/reports_by_day")
    os.environ.setdefault("WORDS_JSON_PATH", "/tmp/words.json")
    os.environ.setdefault("ALL_PAGES_REVIDS_PATH", "/tmp/revids.json")

    # Get the project root directory (parent of pytests folder)
    project_root = Path(__file__).parent.parent

    # Add python_src to sys.path so we can import from 'src' as a package
    python_src_path = project_root  # / "python_src"
    sys.path.insert(0, str(python_src_path))


# Import after environment setup
from src.main_app import create_app
from src.main_app.config import TestingConfig
from src.main_app.shared.auth import CurrentUser
from src.main_app.shared.core.extensions import db as _db


@pytest.fixture(autouse=True)
def disable_network(request, mocker):
    """Disable network requests for non-network tests"""
    if "network" not in request.keywords:
        mocker.patch("requests.get", side_effect=Exception("Network disabled in tests"))
        mocker.patch("requests.post", side_effect=Exception("Network disabled in tests"))
        mocker.patch("urllib.request.urlopen", side_effect=Exception("Network disabled in tests"))


@pytest.fixture
def app() -> Generator[Flask]:
    """Create and configure a test Flask application.

    Yields:
        Flask application configured for testing.
    """
    app = create_app(TestingConfig)

    with app.app_context():
        yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
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


@pytest.fixture
def mock_is_denied(mocker):
    return mocker.patch("src.main_app.shared.core.cors.is_allowed", return_value=None)


@pytest.fixture
def mock_is_allowed(mocker):
    return mocker.patch("src.main_app.shared.core.cors.is_allowed", return_value=None)


@pytest.fixture
def mock_is_allowed_medwiki(mocker):
    return mocker.patch("src.main_app.shared.core.cors.is_allowed", return_value="medwiki.toolforge.org")


@pytest.fixture
def mock_check_secret(mocker):
    return mocker.patch("src.main_app.shared.core.cors.check_publish_secret_code", return_value=None)


@pytest.fixture
def mock_load_request(mocker):
    mock_req = MagicMock()
    mocker.patch("src.main_app.shared.core.cors._load_request", return_value=mock_req)
    return mock_req


@pytest.fixture
def db_config():
    """Fixture for DbConfig instance."""
    from src.main_app.config import DbConfig

    return DbConfig(
        db_name="test_db",
        db_host="localhost",
        db_user="user",
        db_password="pass",
    )


@pytest.fixture(autouse=True)
def setup_db(app: Flask):
    """
    Initialize an in-memory SQLite database for tests using Flask-SQLAlchemy.

    Creates all real tables (skipping views) and creates views manually.
    The Flask-SQLAlchemy session (db.session) is used throughout tests.
    """
    with app.app_context():
        # Create only real tables; skip view-backed mapped classes
        real_tables = [t for t in _db.metadata.tables.values() if not t.info.get("is_view")]
        _db.metadata.create_all(_db.engine, tables=real_tables)

        # Create views manually (SQLite-compatible CREATE VIEW).
        # The ``after_create`` listener in ``extensions`` already creates
        # registered views idempotently; this loop is a fallback for any
        # views that were not created by the listener (e.g. views added
        # without listener support). Skip views that already exist.
        from sqlalchemy import inspect as sa_inspect

        existing_views = set(sa_inspect(_db.engine).get_view_names())
        with _db.engine.connect() as conn:
            for table in _db.metadata.tables.values():
                if not (table.info.get("is_view") and table.info.get("create_query")):
                    continue
                if table.name in existing_views:
                    continue
                try:
                    conn.execute(_db.text(table.info["create_query"]))
                    conn.commit()
                except SQLAlchemyError as exc:
                    conn.rollback()
                    raise RuntimeError(
                        f"Failed to create view {table.name!r} during test setup. "
                        f"create_query={table.info['create_query']!r}"
                    ) from exc

        yield

        _db.session.remove()

        # Drop views first (SQLite requires DROP VIEW, not DROP TABLE)
        with _db.engine.connect() as conn:
            for table in _db.metadata.tables.values():
                if table.info.get("is_view"):
                    try:
                        conn.execute(_db.text(f"DROP VIEW IF EXISTS {table.name}"))
                    except SQLAlchemyError as exc:
                        logging.getLogger(__name__).warning(
                            "Failed to drop view %s during teardown: %s", table.name, exc
                        )
            conn.commit()

        # Drop only real tables
        real_tables = [t for t in _db.metadata.tables.values() if not t.info.get("is_view")]
        _db.metadata.drop_all(_db.engine, tables=real_tables)


@pytest.fixture
def mock_admin_required(mocker):
    """Mock admin_required decorator to bypass authentication checks.

    Inject this fixture into admin route tests to bypass authentication
    so tests can focus on route functionality rather than auth.
    """
    # Mock current_user to return a valid user object
    mock_user = CurrentUser(user_id=0, username="ADMIN_USER", access_token="", access_secret="", is_active_admin=True)
    mocker.patch("src.main_app.admin.decorators.current_user", return_value=mock_user)
