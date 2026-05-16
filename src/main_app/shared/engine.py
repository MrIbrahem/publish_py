"""
engine.py
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import Text, create_engine, event, inspect, text
from sqlalchemy.dialects.mysql import LONGTEXT as LONGTEXTSQLALCHEMY
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.types import TypeDecorator

from .core.extensions import db

logger = logging.getLogger(__name__)


class LONGTEXT(TypeDecorator):
    """LONGTEXT for MySQL, Text for everything else."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "mysql":
            return dialect.type_descriptor(LONGTEXTSQLALCHEMY())
        return dialect.type_descriptor(Text())

# ---------------------------------------------------------------------------
# 2. Database connection — replaces db_driver.py entirely
#    pool_pre_ping=True handles reconnect + retry automatically
# ---------------------------------------------------------------------------


def build_db_url(db_data: dict[str, str]) -> str:
    """

    db_name: str
    db_host: str
    db_user: str | None
    db_password: str | None
    """
    db_user = db_data["db_user"]
    db_password = db_data["db_password"]
    db_host = db_data["db_host"]
    db_name = db_data["db_name"]
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"


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
                    "collation": "utf8mb4_unicode_ci",
                },
            }
        )
    return create_engine(db_url, **kwargs)


# ---------------------------------------------------------------------------
# 3. SessionFactory singleton — replaces _COORDINATORS_STORE
# ---------------------------------------------------------------------------


_SessionFactory: sessionmaker | None = None

# -----------------------------------------------------------------------------
# Create views automatically when tables are created
# -----------------------------------------------------------------------------


@event.listens_for(db.metadata, "after_create")
def create_views_new_all_view(target, connection, **kw):
    inspector = inspect(connection)
    existing_views = inspector.get_view_names()

    views_to_create = {
        table.name: table.info.get("create_query")
        for table in target.tables.values()
        if table.info.get("is_view") and table.info.get("create_query")
    }

    views_to_create[
        "users_list"
    ] = """
        CREATE VIEW users_list AS
            select
                u.user_id AS user_id,
                u.username AS username,
                u.wiki AS wiki,
                u.user_group AS user_group,
                u.reg_date AS reg_date
            from
                users u
    """

    for name, query in views_to_create.items():
        if name not in existing_views:
            try:
                connection.execute(text(query))
                logger.info(f"Successfully created view: {name}")
            except Exception as e:
                logger.exception(f"Error creating view {name}", exc_info=True)
        else:
            logger.info(f"View '{name}' already exists, skipping.")


__all__ = [
    "LONGTEXT",
]
