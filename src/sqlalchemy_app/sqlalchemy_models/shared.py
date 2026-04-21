"""
Shared domain models - SQLAlchemy ORM.

Note: Several models have been moved to specialized modules:
- pages_models.py: PageRecord, UserPageRecord
- qid_models.py: QidRecord
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, func

from ..shared.engine import LONGTEXT, BaseDb

logger = logging.getLogger(__name__)


class CategoryRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS categories (
        id int unsigned NOT NULL AUTO_INCREMENT,
        category varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        campaign varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        display varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        category2 varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        depth int NOT NULL DEFAULT '0',
        is_default int NOT NULL DEFAULT '0',
        PRIMARY KEY (id),
        UNIQUE KEY category (category)
    )
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(120), unique=True, nullable=False)
    campaign = Column(String(120), nullable=False, default="")
    display = Column(String(120), nullable=False, default="")
    category2 = Column(String(120), nullable=False, default="")
    depth = Column(Integer, nullable=False, default=0)
    is_default = Column(Integer, nullable=False, default=0)

    def __init__(self, **kwargs):
        # Apply Python-level defaults for fields not provided
        if "display" not in kwargs:
            kwargs["display"] = ""
        if "category2" not in kwargs:
            kwargs["category2"] = ""
        if "depth" not in kwargs:
            kwargs["depth"] = 0
        if "is_default" not in kwargs:
            kwargs["is_default"] = 0

        # Convert depth and is_default to int
        if "depth" in kwargs:
            kwargs["depth"] = int(kwargs["depth"]) if kwargs["depth"] is not None else 0
        if "is_default" in kwargs:
            kwargs["is_default"] = int(kwargs["is_default"]) if kwargs["is_default"] is not None else 0

        super().__init__(**kwargs)

        # Validate that required fields are not empty
        if not self.category:
            raise ValueError("Category name cannot be empty")

        if not self.campaign:
            raise ValueError("Campaign name cannot be empty")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "campaign": self.campaign,
            "display": self.display,
            "category2": self.category2,
            "depth": self.depth,
            "is_default": self.is_default,
        }


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

    def to_dict(self) -> dict[str, Any]:
        """Convert a ReportRecord to a dictionary."""
        # Handle date conversion with None safety
        if self.date is None:
            date_str = ""
        elif hasattr(self.date, "isoformat"):
            date_str = self.date.isoformat()
        else:
            date_str = str(self.date)

        return {
            "id": self.id,
            "date": date_str,
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "sourcetitle": self.sourcetitle,
            "result": self.result,
            "data": self.data,
        }


__all__ = [
    "ReportRecord",
    "CategoryRecord",
]
