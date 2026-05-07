"""
All Articles domain models - SQLAlchemy ORM.
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String

from ..shared.engine import BaseDb


class AllArticlesRecord(BaseDb):
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(String(255), unique=True, nullable=False)
    category = Column(String(255), nullable=True)


__all__ = [
    "AllArticlesRecord",
]
