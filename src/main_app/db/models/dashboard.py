"""
SQLAlchemy ORM models
"""

from __future__ import annotations

import logging

from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column

from ...shared.core.extensions import db

logger = logging.getLogger(__name__)


class CategoryRecord(db.Model):
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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    campaign: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default=text("''"))
    display: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default=text("''"))
    category2: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default=text("''"))
    depth: Mapped[int] = mapped_column(nullable=False, default=0, server_default=text("0"))
    is_default: Mapped[int] = mapped_column(nullable=False, default=0, server_default=text("0"))

    def __init__(self, **kwargs) -> None:
        # Convert depth and is_default to int if provided as strings
        for key in ("depth", "is_default"):
            kwargs[key] = int(kwargs.get(key, 0))

        # Apply Python-level defaults for fields not provided
        if "display" not in kwargs:
            kwargs["display"] = ""
        if "category2" not in kwargs:
            kwargs["category2"] = ""

        super().__init__(**kwargs)

        # Validate that required fields are not empty
        if not self.category:
            raise ValueError("Category name cannot be empty")

        if not self.campaign:
            raise ValueError("Campaign name cannot be empty")


class ProjectRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS projects (
        g_id int unsigned NOT NULL AUTO_INCREMENT,
        g_title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        PRIMARY KEY (g_id),
        UNIQUE KEY g_title (g_title)
    )
    """

    __tablename__ = "projects"

    g_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    g_title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)


__all__ = [
    "CategoryRecord",
    "ProjectRecord",
]
