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
from typing import Any

from flask import Blueprint, Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import MetaData

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


__all__ = [
    "db",
    "migrate",
    "csrf",
    "csrf_init_app",
    "csrf_exempt",
]
