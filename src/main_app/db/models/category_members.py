"""
CategoryMember domain model — many-to-many membership between categories and articles.

Distinct from ``AllArticlesRecord`` (which has ``UNIQUE(article_id)`` and stores
each article's primary category): ``CategoryMemberRecord`` has
``UNIQUE(category, article_id)`` and is the source of truth for "which articles
belong to category X" — used by the results_2026 and missing-stats flows.
"""

from __future__ import annotations

from ...shared.core.extensions import db


class CategoryMemberRecord(db.Model):
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
        db.UniqueConstraint("category", "article_id", name="category_article_id"),
        db.Index("article_id", "article_id"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(
        db.String(120),
        # db.ForeignKey("categories.category"),
        nullable=False,
    )
    article_id = db.Column(db.String(255), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "article_id": self.article_id,
        }


__all__ = [
    "CategoryMemberRecord",
]
