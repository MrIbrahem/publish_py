"""Configuration and fixtures for pytest"""

import os
import sys
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient
from sqlalchemy import Column, Date, DateTime, Integer, MetaData, String, Table, UniqueConstraint, func, text
from sqlalchemy.orm import sessionmaker

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
from src.sqlalchemy_app import create_app
from src.sqlalchemy_app.config import TestingConfig


@pytest.fixture
def app() -> Generator[Flask, Any, None]:
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
    return mocker.patch("src.sqlalchemy_app.shared.core.cors.is_allowed", return_value=None)


@pytest.fixture
def mock_is_allowed(mocker):
    return mocker.patch("src.sqlalchemy_app.shared.core.cors.is_allowed", return_value=None)


@pytest.fixture
def mock_check_secret(mocker):
    return mocker.patch("src.sqlalchemy_app.shared.core.cors.check_publish_secret_code", return_value=None)


@pytest.fixture
def mock_load_request(mocker):
    mock_req = MagicMock()
    mocker.patch("src.sqlalchemy_app.shared.core.cors._load_request", return_value=mock_req)
    return mock_req


@pytest.fixture
def db_config():
    """Fixture for DbConfig instance."""
    from src.sqlalchemy_app.config import DbConfig

    return DbConfig(
        db_name="test_db",
        db_host="localhost",
        db_user="user",
        db_password="pass",
    )


@pytest.fixture(autouse=True)
def setup_db():
    """Initialize an in-memory SQLite database for tests."""
    from src.sqlalchemy_app.shared import engine as engine_mod
    from src.sqlalchemy_app.shared.engine import (
        BaseDb,
        build_engine,
        init_db,
    )

    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")

    meta = MetaData()
    pages_users = Table(
        "pages_users",
        meta,
        Column("id", Integer, primary_key=True),
        Column("title", String(120), nullable=False),
        Column("word", Integer, nullable=True),
        Column("translate_type", String(20), nullable=True),
        Column("cat", String(120), nullable=True),
        Column("lang", String(30), nullable=True),
        Column("user", String(120), nullable=True),
        Column("target", String(120), nullable=True),
        Column("date", Date, nullable=True),
        Column("pupdate", String(120), nullable=True),
        Column("add_date", DateTime, nullable=False, server_default=func.current_timestamp()),
        Column("deleted", Integer, nullable=False, server_default=text("0")),
        Column("mdwiki_revid", Integer, nullable=True),
    )
    pages_users.create(engine)

    # Create views_new table first (needed for views_new_all view)
    views_new = Table(
        "views_new",
        meta,
        Column("id", Integer, primary_key=True),
        Column("target", String(120), nullable=False),
        Column("lang", String(30), nullable=False),
        Column("year", Integer, nullable=False),
        Column("views", Integer, nullable=True),
        UniqueConstraint("target", "lang", "year", name="target_lang_year"),
    )
    views_new.create(engine)

    # Create views_new_all as a view
    with engine.connect() as conn:
        conn.execute(
            text(
                """
            CREATE VIEW IF NOT EXISTS views_new_all AS
            SELECT target, lang, SUM(views) as views
            FROM views_new
            GROUP BY target, lang
        """
            )
        )
        conn.commit()

    # Create all other tables except views_new_all (which is already created as a view)
    for table in BaseDb.metadata.sorted_tables:
        if table.name != "views_new_all":
            table.create(engine, checkfirst=True)

    factory = sessionmaker(bind=engine, expire_on_commit=False)

    with patch.object(engine_mod, "_SessionFactory", factory):
        yield

    engine.dispose()


@pytest.fixture
def mock_admin_required(mocker):
    """Mock admin_required decorator to bypass authentication checks.

    This fixture automatically applies to all tests in this directory,
    allowing tests to focus on route functionality rather than auth.
    """
    mock_req = MagicMock()
    mock_req.username = "admin"
    mocker.patch("src.sqlalchemy_app.admin.decorators._get_cached_active_coordinators", return_value={
        "admin": mock_req,
    })
    mocker.patch("src.sqlalchemy_app.admin.decorators.current_user", return_value=mock_req)
