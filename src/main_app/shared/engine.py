"""
"""

from __future__ import annotations

import logging

from sqlalchemy import Text, event, inspect, text
from sqlalchemy.dialects.mysql import LONGTEXT as LONGTEXTSQLALCHEMY
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
