import logging

from ...config import DbConfig
from ...shared.core.db_driver import Database
from .db.schema import admin_sql_tables

logger = logging.getLogger(__name__)


def ensure_admin_db_tables(db_data: DbConfig) -> None:
    with Database(db_data) as db:
        db.execute_query_safe(admin_sql_tables.coordinators)
        db.execute_query_safe(admin_sql_tables.full_translators)
        db.execute_query_safe(admin_sql_tables.language_settings)
        db.execute_query_safe(admin_sql_tables.settings)
        db.execute_query_safe(admin_sql_tables.settings1)
        db.execute_query_safe(admin_sql_tables.users_no_inprocess)
