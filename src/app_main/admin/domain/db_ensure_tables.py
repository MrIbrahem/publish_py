import logging

from ...config import DbConfig
from .db.schema import admin_sql_tables
from ...shared.core.db_driver import Database

logger = logging.getLogger(__name__)


def ensure_db_tables(db_data: DbConfig) -> None:
    db = Database(db_data)

    db.execute_query_safe(admin_sql_tables.coordinator)
    db.execute_query_safe(admin_sql_tables.full_translators)
    db.execute_query_safe(admin_sql_tables.language_settings)
    db.execute_query_safe(admin_sql_tables.settings)
    db.execute_query_safe(admin_sql_tables.users_no_inprocess)
