"""
All Articles domain models - SQLAlchemy ORM.
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ...shared.core.extensions import db


class AllArticlesRecord(db.Model):
    """
    CREATE TABLE all_articles (
        id int NOT NULL AUTO_INCREMENT,
        article_id varchar(255) NOT NULL,
        category varchar(255) DEFAULT NULL,
        PRIMARY KEY (id),
        UNIQUE KEY article_id (article_id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
    """

    __tablename__ = "all_articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(255))


__all__ = [
    "AllArticlesRecord",
]
