"""
SQLAlchemy-based service for the ``pages_users_to_main`` admin workflow.

Mirrors the PHP code under ``coordinator/admin/pages_users_to_main/*.php``:
- Lists user pages awaiting promotion to main pages (with proposed new
  ``target`` / ``user`` / ``qid`` overrides).
- Provides the helpers used by the "fix it" form to validate the move and
  delete the source rows once the new main page row has been written.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ....shared.core.extensions import db
from ...models import PageRecord, PagesUsersToMainRecord, QidRecord, UserPageRecord

logger = logging.getLogger(__name__)


def _row_to_dict(row: Any) -> Dict[str, Any]:
    """Convert a result row (tuple of columns from a join) into a dict."""
    if hasattr(row, "_asdict"):
        return dict(row._asdict())
    return dict(row)


def list_pending(lang: str = "All") -> List[Dict[str, Any]]:
    """Return user pages flagged for promotion to main pages.

    Mirrors PHP ``get_pages_users_to_main($lang)``: an inner join between
    ``pages_users`` and ``pages_users_to_main`` (with the QID looked up on
    ``qids.title``), optionally filtered by language.
    """
    query = (
        db.session.query(
            UserPageRecord.id.label("id"),
            UserPageRecord.user.label("user"),
            UserPageRecord.lang.label("lang"),
            UserPageRecord.title.label("title"),
            UserPageRecord.target.label("target"),
            UserPageRecord.pupdate.label("pupdate"),
            PagesUsersToMainRecord.new_user.label("new_user"),
            PagesUsersToMainRecord.new_target.label("new_target"),
            PagesUsersToMainRecord.new_qid.label("new_qid"),
            QidRecord.qid.label("qid"),
        )
        .join(PagesUsersToMainRecord, PagesUsersToMainRecord.id == UserPageRecord.id)
        .outerjoin(QidRecord, QidRecord.title == UserPageRecord.title)
    )
    if lang and lang != "All":
        query = query.filter(UserPageRecord.lang == lang)

    return [
        {
            "id": row.id,
            "user": row.user or "",
            "lang": row.lang or "",
            "title": row.title or "",
            "target": row.target or "",
            "pupdate": row.pupdate or "",
            "new_user": row.new_user or "",
            "new_target": row.new_target or "",
            "new_qid": row.new_qid or "",
            "qid": row.qid or "",
        }
        for row in query.order_by(UserPageRecord.id.asc()).all()
    ]


def get_user_page(page_id: int) -> Optional[UserPageRecord]:
    """Return the ``pages_users`` row for the given id."""
    if not page_id:
        return None
    return db.session.get(UserPageRecord, page_id)


def check_main_page_exists(title: str, lang: str) -> Optional[PageRecord]:
    """Return the first non-empty-target ``pages`` row for (title, lang).

    Used to warn that a duplicate exists before the move.
    """
    if not title or not lang:
        return None
    return (
        db.session.query(PageRecord)
        .filter(
            PageRecord.title == title,
            PageRecord.lang == lang,
            PageRecord.target.isnot(None),
            PageRecord.target != "",
        )
        .first()
    )


def delete_user_page(page_id: int) -> bool:
    """Delete the row from both ``pages_users_to_main`` and ``pages_users``.

    Returns True only when both rows are gone after the operation.
    """
    if not page_id:
        return False

    try:
        db.session.query(PagesUsersToMainRecord).filter(PagesUsersToMainRecord.id == page_id).delete(
            synchronize_session=False
        )
        db.session.query(UserPageRecord).filter(UserPageRecord.id == page_id).delete(synchronize_session=False)
        db.session.commit()
    except Exception:
        logger.exception("Failed to delete pages_users(_to_main) id=%r", page_id)
        db.session.rollback()
        return False

    in_users = db.session.get(UserPageRecord, page_id)
    in_to_main = db.session.get(PagesUsersToMainRecord, page_id)
    return in_users is None and in_to_main is None


__all__ = [
    "list_pending",
    "get_user_page",
    "check_main_page_exists",
    "delete_user_page",
]
