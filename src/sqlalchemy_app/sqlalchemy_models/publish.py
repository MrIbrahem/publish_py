"""
SQLAlchemy ORM models
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, func

from ..shared.engine import LONGTEXT, BaseDb

logger = logging.getLogger(__name__)


class ReportRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS publish_reports (
        id int NOT NULL AUTO_INCREMENT,
        date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        user varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        lang varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        sourcetitle varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        result varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        data longtext CHARACTER
        SET
            utf8mb4 COLLATE utf8mb4_bin NOT NULL,
            PRIMARY KEY (id),
            CONSTRAINT publish_reports_chk_1 CHECK (json_valid (data))
    )
    """

    __tablename__ = "publish_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    title = Column(String(255), nullable=False)
    user = Column(String(255), nullable=False)
    lang = Column(String(255), nullable=False)
    sourcetitle = Column(String(255), nullable=False)
    result = Column(String(255), nullable=False)

    # Compiler <sqlalchemy.dialects.sqlite.base.SQLiteTypeCompiler object at ...> can't render element of type LONGTEXT
    data = Column(LONGTEXT, nullable=False)


__all__ = [
    "ReportRecord",
]
