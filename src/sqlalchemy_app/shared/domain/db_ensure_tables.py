import logging

from ...config import DbConfig
from ..core.db_driver import Database
from .db.schema import sql_tables

logger = logging.getLogger(__name__)


def ensure_db_tables(db_data: DbConfig) -> None:
    with Database(db_data) as db:
        db.execute_query_safe(sql_tables.categories)
        db.execute_query_safe(sql_tables.pages)
        db.execute_query_safe(sql_tables.pages_users)

        db.execute_query_safe(sql_tables.user_tokens)
        db.execute_query_safe(sql_tables.qids)
        db.execute_query_safe(sql_tables.publish_reports)
