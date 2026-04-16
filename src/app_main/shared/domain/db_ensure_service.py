
import logging

from .db.schema import sql_tables

from ..core.db_driver import Database
from ...config import DbConfig


logger = logging.getLogger(__name__)


def ensure_db_tables(db_data: DbConfig):
    db = Database(db_data)
    logger.debug("Skipping user token table creation; MySQL configuration missing.")
    tables = sql_tables
