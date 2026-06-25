"""
Flask data base initialization.
"""

from __future__ import annotations

import logging
from typing import Any

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy import MetaData, Text, event, inspect, text
from sqlalchemy.dialects.mysql import LONGTEXT as LONGTEXTSQLALCHEMY
from sqlalchemy.engine import Connection, Dialect
from sqlalchemy.types import TypeDecorator, TypeEngine


class LONGTEXT(TypeDecorator):
    """LONGTEXT for MySQL, Text for everything else."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine:
        if dialect.name == "mysql":
            return dialect.type_descriptor(LONGTEXTSQLALCHEMY())
        return dialect.type_descriptor(Text())


logger = logging.getLogger(__name__)


class BaseModel(Model):
    """Base model providing a generic to_dict() for all records."""

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for column in self.__table__.columns:  # type: ignore
            value = getattr(self, column.name)  # type: ignore
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            data[column.name] = value  # type: ignore
        return data

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


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
db = SQLAlchemy(
    model_class=BaseModel,
    metadata=metadata,
)


@event.listens_for(db.metadata, "after_create")
def create_views_new_all_view(target: MetaData, connection: Connection, **kw: Any) -> None:
    inspector = inspect(connection)
    existing_views = inspector.get_view_names()

    views_to_create = {
        table.name: table.info.get("create_query")
        for table in target.tables.values()
        if table.info.get("is_view") and table.info.get("create_query")
    }

    for name, query in views_to_create.items():
        if name not in existing_views:
            try:
                connection.execute(text(query))
                logger.info(f"Successfully created view: {name}")
            except Exception:
                logger.exception(f"Error creating view {name}", exc_info=True)
        else:
            logger.info(f"View '{name}' already exists, skipping.")


__all__ = [
    "db",
    "metadata",
    "LONGTEXT",
]
