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
from typing import Any

from ....extensions import db
from ...models import PageRecord, PagesUsersToMainRecord, QidRecord, UserPageRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class PagesUsersToMainPagesService(CRUDService[PagesUsersToMainRecord]):
    model = PagesUsersToMainRecord

    def __init__(self):
        super().__init__(db.session, PagesUsersToMainRecord)


pages_users_to_main_pages_crud = PagesUsersToMainPagesService()


def _row_to_dict(row: Any) -> dict[str, Any]:
    """Convert a result row (tuple of columns from a join) into a dict."""
    if hasattr(row, "_asdict"):
        return dict(row._asdict())
    return dict(row)


def list_pending(lang: str = "All") -> list[dict[str, Any]]:
    """Return user pages flagged for promotion to main pages.

    Mirrors PHP ``get_pages_users_to_main($lang)``: an inner join between
    ``pages_users`` and ``pages_users_to_main`` (with the QID looked up on
    ``qids.title``), optionally filtered by language.
    """
    query = (
        pages_users_to_main_pages_crud.session.query(
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
    if lang and lang.lower() != "all":
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


def get_user_page(page_id: int) -> UserPageRecord | None:
    """Return the ``pages_users`` row for the given id."""
    if not page_id:
        return None
    return pages_users_to_main_pages_crud.session.get(UserPageRecord, page_id)


def check_main_page_exists(title: str, lang: str) -> PageRecord | None:
    """Return the first non-empty-target ``pages`` row for (title, lang).

    Used to warn that a duplicate exists before the move.
    """
    if not title or not lang:
        return None
    return (
        pages_users_to_main_pages_crud.session.query(PageRecord)
        .filter(
            PageRecord.title == title,
            PageRecord.lang == lang,
            PageRecord.target.isnot(None),
            PageRecord.target != "",
        )
        .first()
    )


__all__ = [
    "list_pending",
    "get_user_page",
    "check_main_page_exists",
]
