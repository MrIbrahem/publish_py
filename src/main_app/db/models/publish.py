"""
SQLAlchemy ORM models
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ...shared.core.extensions import LONGTEXT, db

logger = logging.getLogger(__name__)


class ReportRecord(db.Model):
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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(nullable=False, server_default=db.func.current_timestamp())
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    user: Mapped[str] = mapped_column(String(255), nullable=False)
    lang: Mapped[str] = mapped_column(String(255), nullable=False)
    sourcetitle: Mapped[str] = mapped_column(String(255), nullable=False)
    result: Mapped[str] = mapped_column(String(255), nullable=False)

    # Compiler <sqlalchemy.dialects.sqlite.base.SQLiteTypeCompiler object at ...> can't render element of type LONGTEXT
    data: Mapped[str] = mapped_column(LONGTEXT, nullable=False)

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date,
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "sourcetitle": self.sourcetitle,
            "result": self.result,
            "data": self.data,
        }


__all__ = [
    "ReportRecord",
]
