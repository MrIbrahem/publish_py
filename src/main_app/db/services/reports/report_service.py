"""
SQLAlchemy-based service for managing publish reports.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import extract, func, text
from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import ReportRecord

logger = logging.getLogger(__name__)


def list_reports() -> List[ReportRecord]:
    """Return all report records."""
    orm_objs = db.session.query(ReportRecord).order_by(ReportRecord.id.desc()).all()
    return orm_objs


def add_report(
    title: str,
    user: str,
    lang: str,
    sourcetitle: str,
    result: str,
    data: str,
) -> ReportRecord:
    """Add a new report record."""
    orm_obj = ReportRecord(
        title=title,
        user=user,
        lang=lang,
        sourcetitle=sourcetitle,
        result=result,
        data=data,
        date=func.now(),
    )
    db.session.add(orm_obj)
    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def delete_report(report_id: int) -> ReportRecord:
    """Delete a report record by ID."""
    orm_obj = db.session.query(ReportRecord).filter(ReportRecord.id == report_id).first()
    if not orm_obj:
        raise LookupError(f"Report id {report_id} was not found")

    record = ReportRecord(**orm_obj.to_dict())
    db.session.delete(orm_obj)
    db.session.commit()
    return record


def query_reports_with_filters(
    filters: Dict[str, Any],
    select_fields: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> List[ReportRecord]:
    """Query reports with dynamic filtering."""

    COLUMN_MAP = {
        "title": ReportRecord.title,
        "user": ReportRecord.user,
        "lang": ReportRecord.lang,
        "sourcetitle": ReportRecord.sourcetitle,
        "result": ReportRecord.result,
    }

    query = db.session.query(ReportRecord)

    for name, value in filters.items():
        if str(value).lower() == "all":
            continue

        # Year/Month filters
        if name == "year":
            # query = query.filter(db.func.year(ReportRecord.date) == value)
            query = query.filter(extract("year", ReportRecord.date) == int(value))

        elif name == "month":
            # query = query.filter(db.func.month(ReportRecord.date) == value)
            query = query.filter(extract("month", ReportRecord.date) == int(value))
        elif name in COLUMN_MAP:
            # to match ReportsDB methods
            column = COLUMN_MAP[name]
            if value in ("not_mt", "not_empty"):
                query = query.filter(column != "", column.isnot(None))
            elif value in ("mt", "empty"):
                query = query.filter((column == "") | (column.is_(None)))
            elif value in (">0", "&#62;0"):
                # query = query.filter(column > 0)
                # This seems to be for numeric results if any?
                pass
            else:
                query = query.filter(column == value)

    query = query.order_by(ReportRecord.id.desc())

    if limit:
        query = query.limit(limit)

    orm_objs = query.all()

    return orm_objs


__all__ = [
    "list_reports",
    "add_report",
    "delete_report",
    "query_reports_with_filters",
]
