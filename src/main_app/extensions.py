"""
Flask extensions module.

This module contains all Flask extensions used by the application.
"""

from __future__ import annotations

from typing import Any

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text
from sqlalchemy.dialects.mysql import LONGTEXT as LONGTEXTSQLALCHEMY
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.types import TypeDecorator


class LONGTEXT(TypeDecorator):
    """LONGTEXT for MySQL, Text for everything else."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "mysql":
            return dialect.type_descriptor(LONGTEXTSQLALCHEMY())
        return dialect.type_descriptor(Text())


# Initialize Flask-SQLAlchemy
db = SQLAlchemy()

# Initialize Flask-Migrate
migrate = Migrate()


class BaseModelMixin:
    """
    Mixin class that provides common functionality for all models.
    Preserves the to_dict() method from the original BaseDb class.
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert ORM object to dictionary."""
        data = {column.name: getattr(self, column.name) for column in self.__table__.columns}

        # Format date/datetime fields to ISO format strings
        if "add_date" in data and data["add_date"]:
            data["add_date"] = (
                data["add_date"].isoformat() if hasattr(data["add_date"], "isoformat") else str(data["add_date"])
            )

        if "date" in data and data["date"]:
            data["date"] = data["date"].isoformat() if hasattr(data["date"], "isoformat") else str(data["date"])

        # Apply default values for non-nullable columns that are None
        for column in self.__table__.columns:
            if column.nullable is False and data[column.name] is None:
                data[column.name] = column.default

        return data


# Create a base class that combines db.Model with our mixin
class Model(db.Model, BaseModelMixin):
    """Base model class that all models should inherit from."""

    __abstract__ = True


__all__ = [
    "db",
    "migrate",
    "Model",
    "LONGTEXT",
]
