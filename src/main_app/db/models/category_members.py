"""
CategoryMember domain model — many-to-many membership between categories and articles.

Distinct from ``AllArticlesRecord`` (which has ``UNIQUE(article_id)`` and stores
each article's primary category): ``CategoryMemberRecord`` has
``UNIQUE(category, article_id)`` and is the source of truth for "which articles
belong to category X" — used by the results_2026 and missing-stats flows.
"""

from __future__ import annotations

from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ...shared.core.extensions import BaseModel, db


class CategoryMemberRecord(db.Model, BaseModel):
    """
    CREATE TABLE category_members (
        id int NOT NULL AUTO_INCREMENT,
        category varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        article_id varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        PRIMARY KEY (id),
        UNIQUE KEY category_article_id (category, article_id),
        KEY article_id (article_id),
        CONSTRAINT category_members_ibfk_1 FOREIGN KEY (category) REFERENCES categories (category)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
    """

    __tablename__ = "category_members"
    __table_args__ = (
        UniqueConstraint("category", "article_id", name="category_article_id"),
        Index("article_id", "article_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    article_id: Mapped[str] = mapped_column(String(255), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "article_id": self.article_id,
        }


__all__ = [
    "CategoryMemberRecord",
]
