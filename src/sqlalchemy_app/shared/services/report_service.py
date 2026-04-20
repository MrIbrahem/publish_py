"""
SQLAlchemy-based service for managing publish reports.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import extract, func, text
from sqlalchemy.exc import IntegrityError

from ...db_models.shared_models import ReportRecord
from ..engine import get_session
from ..models import _ReportRecord

logger = logging.getLogger(__name__)


def list_reports() -> List[ReportRecord]:
    """Return all report records."""
    with get_session() as session:
        orm_objs = session.query(_ReportRecord).order_by(_ReportRecord.id.desc()).all()
        return [ReportRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def add_report(
    title: str,
    user: str,
    lang: str,
    sourcetitle: str,
    result: str,
    data: str,
) -> ReportRecord:
    """Add a new report record."""
    with get_session() as session:
        orm_obj = _ReportRecord(
            title=title,
            user=user,
            lang=lang,
            sourcetitle=sourcetitle,
            result=result,
            data=data,
            date=func.now(),
        )
        session.add(orm_obj)
        session.commit()
        session.refresh(orm_obj)
        return ReportRecord(**orm_obj.to_dict())


def delete_report(report_id: int) -> ReportRecord:
    """Delete a report record by ID."""
    with get_session() as session:
        orm_obj = session.query(_ReportRecord).filter(_ReportRecord.id == report_id).first()
        if not orm_obj:
            raise LookupError(f"Report id {report_id} was not found")

        record = ReportRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


def query_reports_with_filters(
    filters: Dict[str, Any],
    select_fields: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> List[ReportRecord]:
    """Query reports with dynamic filtering."""

    COLUMN_MAP = {
        "title": _ReportRecord.title,
        "user": _ReportRecord.user,
        "lang": _ReportRecord.lang,
        "sourcetitle": _ReportRecord.sourcetitle,
        "result": _ReportRecord.result,
    }

    with get_session() as session:
        query = session.query(_ReportRecord)

        for name, value in filters.items():
            if str(value).lower() == "all":
                continue

            # Year/Month filters
            if name == "year":
                # query = query.filter(func.year(_ReportRecord.date) == value)
                query = query.filter(extract("year", _ReportRecord.date) == value)

            elif name == "month":
                # query = query.filter(func.month(_ReportRecord.date) == value)
                query = query.filter(extract("month", _ReportRecord.date) == value)
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

        query = query.order_by(_ReportRecord.id.desc())

        if limit:
            query = query.limit(limit)

        orm_objs = query.all()

        return [ReportRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


__all__ = [
    "list_reports",
    "add_report",
    "delete_report",
    "query_reports_with_filters",
]
