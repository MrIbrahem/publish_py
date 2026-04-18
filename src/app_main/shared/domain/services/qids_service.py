"""
Utilities for managing qids
"""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ..db.db_qids import QidsDB
from ..models import QidRecord

logger = logging.getLogger(__name__)

_qid_STORE: QidsDB | None = None


from ....config import has_db_config


def get_qids_db() -> QidsDB:
    global _qid_STORE

    if _qid_STORE is None:
        if not has_db_config():
            raise RuntimeError("QidsDB requires database configuration; no fallback store is available.")

        try:
            _qid_STORE = QidsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL QidsDB")
            raise RuntimeError("Unable to initialize QidsDB") from exc

    return _qid_STORE


def add_qid(title: str, qid: str) -> QidRecord:
    """Add a QID for a title."""
    store = get_qids_db()
    return store.add(title, qid)


def update_qid(qid_id: int, title: str, qid: str) -> QidRecord:
    """Update a QID record."""
    store = get_qids_db()
    record = store.update(qid_id, title, qid)
    return record


def delete_qid(qid_id: int) -> None:
    """Delete a QID record."""
    store = get_qids_db()
    store.delete(qid_id)


def get_page_qid(title: str) -> QidRecord | None:
    """Get the QID for a page title, with caching.

    Args:
        title: MDWiki page title

    Returns:
        QidRecord if found, None otherwise
    """
    store = get_qids_db()
    return store.fetch_by_title(title)


def list_qids() -> List[QidRecord]:
    """Return all QID records."""
    store = get_qids_db()
    records = store.list()
    return records


def get_title_to_qid() -> dict[str, str]:
    """Retrieve title to QID mapping from database.

    Returns:
        Dictionary mapping page titles to QID strings
    """
    qids = list_qids()

    title_to_qid: dict[str, str] = {record.title: record.qid or "" for record in qids}
    return title_to_qid


__all__ = [
    "add_qid",
    "update_qid",
    "delete_qid",
    "get_page_qid",
    "list_qids",
    "get_title_to_qid",
]
