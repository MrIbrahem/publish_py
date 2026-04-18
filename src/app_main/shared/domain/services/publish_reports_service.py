"""
Utilities for managing publish_reports
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ....config import settings
from ..db.db_publish_reports import ReportsDB
from ..models import ReportRecord
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
    title: str,
    user: str,
    lang: str,
    sourcetitle: str,
    result: str,
    data: str,
) -> ReportRecord:
    """Add a report."""

    store = get_publish_reports_db()
    record = store.add(title, user, lang, sourcetitle, result, data)

    return record


def publish_reports_query_with_filters(
    filters: Dict[str, Any],
    select_fields: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> List[ReportRecord]:
    store = get_publish_reports_db()
    records = store.query_with_filters(filters, select_fields, limit)

    return records


def delete_report(report_id: int) -> None:
    """Delete a report."""

    store = get_publish_reports_db()
    store.delete(report_id)


def list_publish_reports() -> List[ReportRecord]:
    """Return all publish_reports."""

    store = get_publish_reports_db()

    coords = store.list()
    return coords


__all__ = [
    "add_report",
    "delete_report",
    "list_publish_reports",
    "publish_reports_query_with_filters",
]
