"""
engine.py - Compatibility layer for Flask-SQLAlchemy migration.

This module provides backward compatibility for code that still uses the old
get_session() pattern. It redirects to Flask-SQLAlchemy's db.session.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager

from sqlalchemy import Text
from sqlalchemy.dialects.mysql import LONGTEXT as LONGTEXTSQLALCHEMY
from sqlalchemy.types import TypeDecorator

from ..extensions import LONGTEXT, Model, db

logger = logging.getLogger(__name__)

# Export compatibility symbols
BaseDb = Model  # For backward compatibility


@contextmanager
def get_session():
    """
    Compatibility wrapper that returns Flask-SQLAlchemy's session.

    This is a temporary compatibility layer. New code should use db.session directly.
    The session is automatically managed by Flask-SQLAlchemy and will be cleaned up
    after the request context ends.

    Usage:
        with get_session() as session:
            session.query(Model).all()
    """
    # Return Flask-SQLAlchemy's session
    # Note: Flask-SQLAlchemy manages the session lifecycle automatically
    session = db.session
    try:
        yield session
        # Flask-SQLAlchemy handles commit automatically, but we keep it for compatibility
        # session.commit() is not needed here as it's handled by Flask-SQLAlchemy's request teardown
    except Exception:
        # Flask-SQLAlchemy handles rollback automatically on exceptions
        session.rollback()
        raise


# Deprecated functions - kept for backward compatibility
def build_db_url(db_data: dict[str, str]) -> str:
    """
    Build database URL from configuration dict.

    DEPRECATED: This function is deprecated. Database URL should be configured
    through Flask-SQLAlchemy's SQLALCHEMY_DATABASE_URI config.
    """
    logger.warning("build_db_url() is deprecated. Use SQLALCHEMY_DATABASE_URI config instead.")
    db_user = db_data["db_user"]
    db_password = db_data["db_password"]
    db_host = db_data["db_host"]
    db_name = db_data["db_name"]
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"


def init_db(db_url: str, create_tables: bool = False) -> None:
    """
    Initialize the database.

    DEPRECATED: This function is deprecated. Database initialization is now
    handled by Flask-SQLAlchemy through db.init_app() in the application factory.
    """
    logger.warning(
        "init_db() is deprecated. Database initialization is handled by Flask-SQLAlchemy. "
        "Use db.init_app(app) in the application factory instead."
    )
    # This function is now a no-op as Flask-SQLAlchemy handles initialization


__all__ = [
    # Compatibility exports
    "BaseDb",  # Alias for Model
    "get_session",
    "LONGTEXT",
    # Deprecated functions
    "build_db_url",
    "init_db",
]
