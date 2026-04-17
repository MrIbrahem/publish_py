"""
engine.py
"""

from __future__ import annotations

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Model — replaces coordinator_model.py + CREATE TABLE
# ---------------------------------------------------------------------------


class BaseDb(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# 2. Database connection — replaces db_driver.py entirely
#    pool_pre_ping=True handles reconnect + retry automatically
# ---------------------------------------------------------------------------


def build_engine(db_url: str):
    """
    Create a SQLAlchemy engine.

    Example db_url:
        "mysql+pymysql://user:pass@host/dbname?charset=utf8mb4"
    """
    return create_engine(
        db_url,
        pool_pre_ping=True,  # replaces _ensure_connection and retry logic
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,  # recycle connections after 1 hour
        connect_args={
            "connect_timeout": 5,
            "init_command": "SET time_zone = '+00:00'",
            "charset": "utf8mb4",
        },
    )


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
        raise RuntimeError("Call init_db() before using the database.")
    return _SessionFactory()


__all__ = [
    # Model
    "BaseDb",
    # Setup
    "init_db",
    "get_session",
]
