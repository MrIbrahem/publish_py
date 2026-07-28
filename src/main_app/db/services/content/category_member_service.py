"""
SQLAlchemy-based service for managing category_members table.
"""

from __future__ import annotations

import logging

from sqlalchemy import text

from ....extensions import db
from ...models import CategoryMemberRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class CategoryMemberService(CRUDService[CategoryMemberRecord, int]):
    model = CategoryMemberRecord


category_member_crud = CategoryMemberService(db.session)


def get_all_category_members() -> dict[str, list[str]]:
    """Return {category: [article_id, ...]} mapping.

    Mirrors old ``sql_for_mdwiki.get_db_category_members()``.
    """
    data: dict[str, list[str]] = {}

    rows = category_member_crud.session.query(CategoryMemberRecord.category, CategoryMemberRecord.article_id).all()
    for category, article_id in rows:
        data.setdefault(category, []).append(article_id)
    return data


def list_distinct_article_ids() -> list[str]:
    """Return distinct article_id values from category_members.

    Mirrors old ``select DISTINCT article_id from category_members``.
    """

    rows = category_member_crud.session.query(CategoryMemberRecord.article_id).distinct().all()
    return [row.article_id for row in rows]


def count_by_category(category: str) -> int:
    """Return the number of members in *category*."""

    return category_member_crud.count(filters={"category": category})


def get_members_by_category(category: str) -> list[CategoryMemberRecord]:
    """Return all member records for *category*."""

    return list(category_member_crud.list(filters={"category": category}))


def add_category_member(category: str, article_id: str) -> bool:
    """Insert a single category member row. Returns True on success."""

    try:
        existing = category_member_crud.get_by(category=category, article_id=article_id)
        if existing:
            return True
        category_member_crud.create(category=category, article_id=article_id)
        return True
    except Exception:
        logger.exception("Failed to add category member %s / %s", category, article_id)
        return False


def batch_sync_category_members(data: list[dict]) -> None:
    """Insert only new category_member rows, skipping existing ones.

    Accepts a list of dicts with keys ``category`` and ``article_id``.
    Mirrors the diff-and-insert pattern from ``all_articles.py``.
    """

    try:
        existing_rows = set(
            category_member_crud.session.query(CategoryMemberRecord.category, CategoryMemberRecord.article_id).all()
        )
        new_rows = []
        seen = set()
        for row in data:
            cat = row.get("category", "")
            aid = row.get("article_id", "")
            if cat and aid and (cat, aid) not in existing_rows and (cat, aid) not in seen:
                new_rows.append({"category": cat, "article_id": aid})
                seen.add((cat, aid))
        if new_rows:
            db.session.execute(
                text(
                    """
                    INSERT INTO category_members (category, article_id)
                    VALUES (:category, :article_id)
                """
                ),
                new_rows,
            )
            db.session.commit()
            logger.info("Inserted %s new category_member rows", len(new_rows))
        else:
            logger.info("No new category_member rows to insert")
    except Exception:
        logger.exception("Failed to sync category members")
        db.session.rollback()
        raise


__all__ = [
    "get_all_category_members",
    "list_distinct_article_ids",
    "count_by_category",
    "get_members_by_category",
    "add_category_member",
    "batch_sync_category_members",
]
