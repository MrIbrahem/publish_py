from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)


class BaseDb(DeclarativeBase):
    """
    Base class for database models.
    Provides common functionality like to_dict.
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert ORM object to dictionary."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


def build_engine(db_url: str):
    """
    Create a SQLAlchemy engine.
    """
    kwargs = {
        "pool_pre_ping": True,
    }
    if not db_url.startswith("sqlite"):
        kwargs.update(
            {
                "pool_size": 5,
                "max_overflow": 10,
                "pool_recycle": 3600,
                "connect_args": {
                    "connect_timeout": 5,
                    "init_command": 'SET time_zone = "+00:00"',
                    "charset": "utf8mb4",
                },
            }
        )
    return create_engine(db_url, **kwargs)


_SessionFactory: sessionmaker | None = None


def init_db(db_url: str) -> None:
    """
    Initialize the engine and SessionFactory.
    """
    global _SessionFactory
    engine = build_engine(db_url)
    _SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Session:
    """Return a new session. Always use inside a with block."""
    if _SessionFactory is None:
        raise RuntimeError("Call init_db() before using the database.")
    return _SessionFactory()


__all__ = [
    "BaseDb",
    "init_db",
    "get_session",
]
