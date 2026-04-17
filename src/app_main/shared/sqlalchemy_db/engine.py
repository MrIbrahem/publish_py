"""
engine.py
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Model — replaces coordinator_model.py + CREATE TABLE
# ---------------------------------------------------------------------------


class BaseDb(DeclarativeBase):
    """
    Base class for database models.
    Provides common functionality like to_dict.
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert ORM object to dictionary."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# ---------------------------------------------------------------------------
# 2. Database connection — replaces db_driver.py entirely
#    pool_pre_ping=True handles reconnect + retry automatically
# ---------------------------------------------------------------------------


def build_engine(db_url: str) -> Engine:
    """
    Create a SQLAlchemy engine.
    """
    kwargs = {
        "pool_pre_ping": True,  # replaces _ensure_connection and retry logic
    }

    if not db_url.startswith("sqlite"):
        kwargs.update(
            {
                "pool_size": 5,
                "max_overflow": 10,
                "pool_recycle": 3600,  # recycle connections after 1 hour
                "connect_args": {
                    "connect_timeout": 5,
                    "init_command": 'SET time_zone = "+00:00"',
                    "charset": "utf8mb4",
                },
            }
        )
    return create_engine(db_url, **kwargs)


# ---------------------------------------------------------------------------
# 3. SessionFactory singleton — replaces _COORDINATORS_STORE
# ---------------------------------------------------------------------------


_SessionFactory: sessionmaker | None = None


def init_db(db_url: str, create_tables: bool = False) -> None:
    """
    Initialize the engine and SessionFactory.
    Call once at application startup.

    create_tables=True: creates the table if it does not exist (useful for testing).
    """
    global _SessionFactory
    engine = build_engine(db_url)
    if create_tables:
        BaseDb.metadata.create_all(engine)
    _SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Session:
    """Return a new session. Always use inside a `with` block."""
    if _SessionFactory is None:
        # For migration purposes, if not initialized, we might need a way to initialize it
        # But according to instructions, we should just use it.
        # In a real app, init_db would be called at startup.
        raise RuntimeError("Call init_db() before using the database.")
    return _SessionFactory()


__all__ = [
    # Model
    "BaseDb",
    # Setup
    "init_db",
    "get_session",
]
