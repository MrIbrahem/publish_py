"""
coordinators_sqlalchemy.py
--------------------------
Experiment: full coordinators table rewritten with SQLAlchemy.
Replaces: coordinator_model.py + db_coordinators.py + coordinators_service.py + db_driver.py
"""

from __future__ import annotations

import functools
import logging
from typing import List

from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Model — replaces coordinator_model.py + CREATE TABLE
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class Coordinator(Base):
    """ORM model for the coordinators table."""

    __tablename__ = "coordinators"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(120, collation="utf8mb4_unicode_ci"), unique=True, nullable=False)
    is_active: int = Column(Integer, nullable=False, default=1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
        }

    def __repr__(self) -> str:
        return f"<Coordinator id={self.id} username={self.username!r} is_active={self.is_active}>"


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
        pool_pre_ping=True,       # replaces _ensure_connection and retry logic
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,        # recycle connections after 1 hour
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
        Base.metadata.create_all(engine)
    _SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Session:
    """Return a new session. Always use inside a `with` block."""
    if _SessionFactory is None:
        raise RuntimeError("Call init_db() before using the database.")
    return _SessionFactory()


# ---------------------------------------------------------------------------
# 4. Service functions — replace coordinators_service.py + db_coordinators.py
# ---------------------------------------------------------------------------

def list_coordinators() -> List[Coordinator]:
    """Return all coordinator records."""
    with get_session() as session:
        return session.query(Coordinator).order_by(Coordinator.id).all()


@functools.lru_cache(maxsize=1)
def active_coordinators() -> List[str]:
    """Return usernames of all active coordinators (cached)."""
    with get_session() as session:
        records = session.query(Coordinator).filter_by(is_active=1).order_by(Coordinator.id).all()
        return [r.username for r in records]


def get_coordinator(coordinator_id: int) -> Coordinator | None:
    """Fetch a coordinator by ID."""
    with get_session() as session:
        result = session.get(Coordinator, coordinator_id)
        if result is None:
            logger.warning("Coordinator record with ID %s not found", coordinator_id)
        return result


def get_coordinator_by_user(username: str) -> Coordinator | None:
    """Fetch a coordinator by username."""
    with get_session() as session:
        return session.query(Coordinator).filter_by(username=username).first()


def add_coordinator(username: str, is_active: int = 1) -> Coordinator:
    """Add a new coordinator. Raises ValueError if username already exists."""
    username = username.strip()
    if not username:
        raise ValueError("username is required")

    with get_session() as session:
        record = Coordinator(username=username, is_active=is_active)
        session.add(record)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Coordinator '{username}' already exists") from None
        active_coordinators.cache_clear()
        return record


def add_or_update_coordinator(username: str, is_active: int = 1) -> Coordinator:
    """Add a coordinator or update is_active if already exists (UPSERT)."""
    username = username.strip()
    if not username:
        raise ValueError("username is required")

    with get_session() as session:
        record = session.query(Coordinator).filter_by(username=username).first()
        if record:
            record.is_active = is_active
        else:
            record = Coordinator(username=username, is_active=is_active)
            session.add(record)
        session.commit()
        active_coordinators.cache_clear()
        return record


def update_coordinator(coordinator_id: int, **kwargs) -> Coordinator:
    """Update fields on a coordinator record. Raises ValueError if not found."""
    with get_session() as session:
        record = session.get(Coordinator, coordinator_id)
        if record is None:
            raise ValueError(f"Coordinator with ID {coordinator_id} not found")
        for key, value in kwargs.items():
            setattr(record, key, value)
        session.commit()
        active_coordinators.cache_clear()
        return record


def delete_coordinator(coordinator_id: int) -> Coordinator:
    """Delete a coordinator and return the record before deletion."""
    with get_session() as session:
        record = session.get(Coordinator, coordinator_id)
        if record is None:
            raise ValueError(f"Coordinator with ID {coordinator_id} not found")
        session.delete(record)
        session.commit()
        active_coordinators.cache_clear()
        return record


def is_coordinator(username: str) -> bool:
    """Return True if the username belongs to an active coordinator."""
    record = get_coordinator_by_user(username)
    return record is not None and record.is_active == 1


def set_coordinator_active(coordinator_id: int, is_active: bool) -> Coordinator:
    """Enable or disable a coordinator."""
    return update_coordinator(coordinator_id, is_active=1 if is_active else 0)


# ---------------------------------------------------------------------------
# __all__
# ---------------------------------------------------------------------------

__all__ = [
    # Model
    "Coordinator",
    "Base",
    # Setup
    "init_db",
    "get_session",
    # Service
    "list_coordinators",
    "active_coordinators",
    "get_coordinator",
    "get_coordinator_by_user",
    "add_coordinator",
    "add_or_update_coordinator",
    "update_coordinator",
    "delete_coordinator",
    "is_coordinator",
    "set_coordinator_active",
  ]
                             
