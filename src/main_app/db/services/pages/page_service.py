"""
SQLAlchemy-based service for managing pages and page targets.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import PageRecord
from ..analytics.word_service import get_word_counts_for_title
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class PagesService(CRUDService[PageRecord, int]):
    model = PageRecord


pages_crud = PagesService(db.session)


def list_translated(lang: str = "All", limit: int = 500, offset: int = 0) -> list[PageRecord]:
    """Return translated pages (target not empty) optionally filtered by language."""
    query = pages_crud.session.query(PageRecord).filter(PageRecord.target.isnot(None), PageRecord.target != "")
    if lang and lang.lower() != "all":
        query = query.filter(PageRecord.lang == lang)
    return query.order_by(PageRecord.id.desc()).limit(limit).offset(offset).all()


def count_translated(lang: str = "All") -> int:
    """Return total count of translated pages, optionally filtered by language."""
    query = pages_crud.session.query(func.count(PageRecord.id)).filter(
        PageRecord.target.isnot(None), PageRecord.target != ""
    )
    if lang and lang.lower() != "all":
        query = query.filter(PageRecord.lang == lang)
    return int(query.scalar() or 0)


def get_by_id(page_id: int) -> PageRecord | None:
    """Return a single page row by id, or None when missing."""
    return pages_crud.get(page_id)


def get_page_by_id(page_id: int) -> PageRecord | None:
    """Return a single page row by id, or None when missing."""
    return pages_crud.get(page_id)


def list_pages() -> list[PageRecord]:
    """Return all pages."""
    return list(
        pages_crud.list(
            order_by=[PageRecord.id.asc()],
        )
    )


def list_pages_by_lang_cat(lang: str, cat: str) -> list[PageRecord]:
    """Return pages filtered by language and category."""
    return list(pages_crud.list(filters={"lang": lang, "cat": cat}))


def add_page(
    sourcetitle: str,
    translate_type: str,
    cat: str,
    lang: str,
    user: str,
    target: str,
    mdwiki_revid: int | None = None,
    word: int = 0,
) -> PageRecord:
    """Add a page and return the created record."""
    if not sourcetitle:
        raise ValueError("Title is required")
    try:
        return pages_crud.create(
            title=sourcetitle,
            word=word,
            translate_type=translate_type,
            cat=cat,
            lang=lang,
            user=user,
            pupdate=func.current_date(),
            target=target,
            mdwiki_revid=mdwiki_revid,
        )
    except IntegrityError as e:
        logger.error(f"Failed to add page (integrity error): {e}")
        raise ValueError(f"Page with title '{sourcetitle}' already exists") from e
    except Exception as e:
        logger.error(f"Failed to add page: {e}")
        raise


def insert_page_target(
    sourcetitle: str,
    translate_type: str,
    cat: str,
    lang: str,
    user: str,
    target: str,
    mdwiki_revid: int | None = None,
    word: int = 0,
) -> bool:
    """Insert a page target record and return success status."""
    try:
        add_page(
            sourcetitle=sourcetitle,
            translate_type=translate_type,
            cat=cat,
            lang=lang,
            user=user,
            target=target,
            mdwiki_revid=mdwiki_revid,
            word=word,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to insert page target: {e}")
        return False


def update_page(
    page_id: int,
    title: str,
    target: str,
    **kwargs: Any,
) -> PageRecord:
    """Update page."""
    try:
        return pages_crud.update(page_id, title=title, target=target, **kwargs)
    except ValueError as exc:
        raise LookupError(f"Page id {page_id} was not found") from exc


def set_page_target(
    record: PageRecord,
    target: str,
) -> bool:
    """ """
    try:
        pages_crud.update(record.id, target=target, pupdate=datetime.now().strftime("%Y-%m-%d"))
        return True
    except Exception:
        logger.exception("Failed to update page target")
        return False


def find_page_record(
    title: str,
    lang: str,
    user: str,
) -> PageRecord | None:
    """
    Check if record exists
    """
    return pages_crud.get_by(title=title, lang=lang, user=user)


def add_translate_row_to_db(
    title: str,
    translate_type: str,
    cat: str,
    lang: str,
    user: str,
    target: str,
    pupdate: str,
    word: int = 0,
) -> bool:
    """Mirror of PHP add_pages_to_db + insert_to_pages.

    Replaces ``_`` with `` `` in string values, UPDATEs rows where target is
    empty, then INSERTs a new row if no matching title+lang+user exists.
    """
    translate_type = translate_type or "lead"
    cat = cat or "RTT"

    if word == 0:
        lead_words, all_words = get_word_counts_for_title(title)
        if translate_type == "all":
            word = all_words or 0
        else:
            word = lead_words or 0

    title = title.replace("_", " ")
    user = user.replace("_", " ")
    target = target.replace("_", " ")
    cat = cat.replace("_", " ")
    lang = lang.replace("_", " ")
    pupdate = pupdate.replace("_", " ")

    try:
        pages_crud.session.query(PageRecord).filter(
            PageRecord.user == user,
            PageRecord.title == title,
            PageRecord.lang == lang,
            or_(PageRecord.target == "", PageRecord.target.is_(None)),
        ).update(
            {PageRecord.target: target, PageRecord.pupdate: pupdate, "word": word},
            synchronize_session=False,
        )
    except Exception:
        logger.exception("Failed to update existing page target")
        pages_crud.session.rollback()
        return False

    existing = pages_crud.get_by(title=title, lang=lang, user=user)

    if not existing:
        try:
            pages_crud.create(
                title=title,
                word=word,
                translate_type=translate_type,
                cat=cat,
                lang=lang,
                user=user,
                target=target,
                pupdate=pupdate,
                date=func.current_date(),
            )
        except Exception:
            logger.exception("Failed to insert new page")
            return False

    found = (
        db.session.query(PageRecord)
        .filter(
            PageRecord.title == title, PageRecord.lang == lang, PageRecord.user == user, PageRecord.target == target
        )
        .first()
    )
    return found is not None


__all__ = [
    "get_page_by_id",
    "set_page_target",
    "find_page_record",
    "list_pages",
    "list_pages_by_lang_cat",
    "add_page",
    "update_page",
    "insert_page_target",
    "add_translate_row_to_db",
]
