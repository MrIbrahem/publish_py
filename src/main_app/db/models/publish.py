"""
SQLAlchemy ORM models
"""

from __future__ import annotations

import logging

from ...shared.core.extensions import LONGTEXT, BaseModel, db

logger = logging.getLogger(__name__)


class ReportRecord(db.Model, BaseModel):
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
    )
    """

    __tablename__ = "publish_reports"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    title = db.Column(db.String(255), nullable=False)
    user = db.Column(db.String(255), nullable=False)
    lang = db.Column(db.String(255), nullable=False)
    sourcetitle = db.Column(db.String(255), nullable=False)
    result = db.Column(db.String(255), nullable=False)

    # Compiler <sqlalchemy.dialects.sqlite.base.SQLiteTypeCompiler object at ...> can't render element of type LONGTEXT
    data = db.Column(LONGTEXT, nullable=False)


__all__ = [
    "ReportRecord",
]
