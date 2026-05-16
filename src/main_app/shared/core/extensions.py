"""
Flask extensions initialization.

This module centralizes Flask extensions to prevent circular imports
and enable proper initialization order with the application factory pattern.

IMPORT RULE: Always import extensions from this module.
Never instantiate extensions elsewhere.

Usage:
    from main_app.shared.core.extensions import db, migrate, csrf
"""

from __future__ import annotations
import logging
from typing import Any

from flask import Blueprint, Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import MetaData, text

from sqlalchemy import Text
from sqlalchemy.dialects.mysql import LONGTEXT as LONGTEXTSQLALCHEMY
from sqlalchemy.types import TypeDecorator

logger = logging.getLogger(__name__)


class LONGTEXT(TypeDecorator):
    """LONGTEXT for MySQL, Text for everything else."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "mysql":
            return dialect.type_descriptor(LONGTEXTSQLALCHEMY())
        return dialect.type_descriptor(Text())


class Base:
    """
    Base class for database models.
    Provides common functionality like to_dict.
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert ORM object to dictionary."""
        data = {column.name: getattr(self, column.name) for column in self.__table__.columns}

        if "add_date" in data and self.add_date:
            data["add_date"] = self.add_date.isoformat() if hasattr(self.add_date, "isoformat") else str(self.add_date)

        if "date" in data and self.date:
            data["date"] = self.date.isoformat() if hasattr(self.date, "isoformat") else str(self.date)

        for column in self.__table__.columns:
            if column.nullable is False and data[column.name] is None:
                data[column.name] = column.default

        return data


# Naming convention for constraints (required for reliable Alembic migrations)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

# Flask-SQLAlchemy instance
# Uses existing BaseDb (DeclarativeBase) as model_class so all existing
# models continue to work unchanged.
db = SQLAlchemy(metadata=metadata, model_class=Base)

# Flask-Migrate instance (Alembic integration)
migrate = Migrate()

# CSRF Protection
csrf = CSRFProtect()


def csrf_init_app(app: Flask) -> None:
    """Initialize CSRF protection."""
    csrf.init_app(app)


def csrf_exempt(app: Flask, bp_publish: Blueprint) -> None:
    """Exempt a blueprint from CSRF protection."""
    if app.config.get("WTF_CSRF_ENABLED"):
        csrf.exempt(bp_publish)


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
    "db",
    "migrate",
    "csrf",
    "csrf_init_app",
    "csrf_exempt",
]
