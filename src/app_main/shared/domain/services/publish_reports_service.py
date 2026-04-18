"""
Utilities for managing publish_reports
"""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ..db.db_publish_reports import ReportsDB
from ..models import CategoryRecord
from ..db_service import has_db_config

logger = logging.getLogger(__name__)

_publish_reports_STORE: ReportsDB | None = None


def get_publish_reports_db() -> ReportsDB:
    global _publish_reports_STORE

    if _publish_reports_STORE is None:
        if not has_db_config():
            raise RuntimeError("ReportsDB requires database configuration; no fallback store is available.")

        try:
            _publish_reports_STORE = ReportsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL ReportsDB")
            raise RuntimeError("Unable to initialize ReportsDB") from exc

    return _publish_reports_STORE


def add_report(
    category: str,
    display: str | None = "",
    campaign: str | None = "",
    category2: str | None = "",
    depth: int = 0,
    is_default: int = 0,
) -> CategoryRecord:
    """Add a category."""

    # fallback display to campaign name if display name is not provided
    display = display or campaign

    store = get_publish_reports_db()
    record = store.add(category, display, campaign, category2, depth)

    if is_default:
        # set this category as default by unsetting default flag on all other publish_reports
        store.set_default(record.id)

    return record


def update_report(report_id: int, title: str, main_file: str) -> CategoryRecord:
    """Update category."""

    store = get_publish_reports_db()
    record = store.update(report_id, title, main_file)

    return record


def delete_report(report_id: int) -> None:
    """Delete a category."""

    store = get_publish_reports_db()
    store.delete(report_id)


def list_publish_reports() -> List[CategoryRecord]:
    """Return all publish_reports."""

    store = get_publish_reports_db()

    coords = store.list()
    return coords


__all__ = [
    "add_report",
    "update_report",
    "delete_report",
    "list_publish_reports",
]
