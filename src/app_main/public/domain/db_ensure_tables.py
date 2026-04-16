import logging

from ...shared.core.db_driver import Database

from ...config import DbConfig
from .db.schema import public_sql_tables

logger = logging.getLogger(__name__)


def ensure_public_db_tables(db_data: DbConfig) -> None:
    with Database(db_data) as db:
        db.execute_query_safe(public_sql_tables.assessments)
        db.execute_query_safe(public_sql_tables.enwiki_pageviews)
        db.execute_query_safe(public_sql_tables.in_process)
        db.execute_query_safe(public_sql_tables.langs)
        db.execute_query_safe(public_sql_tables.mdwiki_revids)
        db.execute_query_safe(public_sql_tables.pages_users_to_main)
        db.execute_query_safe(public_sql_tables.projects)
        db.execute_query_safe(public_sql_tables.refs_counts)
        db.execute_query_safe(public_sql_tables.translate_type)
        db.execute_query_safe(public_sql_tables.users)
        db.execute_query_safe(public_sql_tables.views_new)
        db.execute_query_safe(public_sql_tables.words)
