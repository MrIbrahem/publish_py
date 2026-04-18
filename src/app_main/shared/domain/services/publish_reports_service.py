"""
Utilities for managing publish_reports
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ....config import has_db_config, settings
from ..db.db_publish_reports import ReportsDB
from .....db_models.shared_models import ReportRecord

logger = logging.getLogger(__name__)

_REPORTS_STORE: ReportsDB | None = None


def get_publish_reports_db() -> ReportsDB:
    global _REPORTS_STORE

    if _REPORTS_STORE is None:
        if not has_db_config():
            raise RuntimeError("ReportsDB requires database configuration; no fallback store is available.")

        try:
            _REPORTS_STORE = ReportsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL ReportsDB")
            raise RuntimeError("Unable to initialize ReportsDB") from exc

    return _REPORTS_STORE


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


def query_reports_with_filters(
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


def list_reports() -> List[ReportRecord]:
    """Return all publish_reports."""

    store = get_publish_reports_db()

    pages = store.list()
    return pages


__all__ = [
    "add_report",
    "delete_report",
    "list_reports",
    "query_reports_with_filters",
]
