"""
SQLAlchemy ORM models
"""

from __future__ import annotations

import logging

from sqlalchemy import Column, Integer, String

from ..shared.engine import BaseDb

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


class ProjectRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS projects (
        g_id int unsigned NOT NULL AUTO_INCREMENT,
        g_title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        PRIMARY KEY (g_id),
        UNIQUE KEY g_title (g_title)
    )
    """

    __tablename__ = "projects"

    g_id = Column(Integer, primary_key=True, autoincrement=True)
    g_title = Column(String(120), unique=True, nullable=False)


__all__ = [
    "CategoryRecord",
    "ProjectRecord",
]
