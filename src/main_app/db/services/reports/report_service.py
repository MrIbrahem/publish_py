"""
SQLAlchemy-based service for managing publish reports.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import Numeric, cast, extract, func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.types import Integer as SAInteger
from sqlalchemy.types import Numeric as SANumeric

from ....extensions import db
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
                # Apply a numeric ">0" predicate. For string columns,
                # cast to integer so the comparison is meaningful in SQL.
                # If the column type is unknown / non-comparable, raise.
                """col_type = getattr(column, "type", None)
                if isinstance(col_type, (SAInteger, SANumeric)):
                    query = query.filter(column > 0)
                else:
                    try:
                        query = query.filter(cast(column, SAInteger) > 0)
                    except Exception as exc:
                        raise ValueError(
                            f"Filter '>0' is not supported for column '{name}' of type {col_type!r}"
                        ) from exc"""
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
    "query_reports_with_filters",
]
