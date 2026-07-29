"""
SQLAlchemy-based service for managing publish reports.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import extract, func

from ....extensions import db
from ...models import ReportRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class ReportService(CRUDService[ReportRecord]):
    model = ReportRecord

    def __init__(self):
        super().__init__(db.session, ReportRecord)

    def list_reports(
        self,
    ) -> list[ReportRecord]:
        """Return all report records."""
        return list(
            self.list(
                order_by=[ReportRecord.id.desc()],
            )
        )

    def add_report(
        self,
        title: str,
        user: str,
        lang: str,
        sourcetitle: str,
        result: str,
        data: str,
    ) -> ReportRecord:
        """Add a new report record."""
        return self.create(
            title=title,
            user=user,
            lang=lang,
            sourcetitle=sourcetitle,
            result=result,
            data=data,
            date=func.now(),
        )

    def query_reports_with_filters(
        self,
        filters: dict[str, Any],
        select_fields: list[str] | None = None,
        limit: int | None = None,
    ) -> list[ReportRecord]:
        """Query reports with dynamic filtering."""

        COLUMN_MAP = {
            "title": ReportRecord.title,
            "user": ReportRecord.user,
            "lang": ReportRecord.lang,
            "sourcetitle": ReportRecord.sourcetitle,
            "result": ReportRecord.result,
        }

        query = self.session.query(ReportRecord)

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
                    logger.debug("Filter '>0' is not supported for column '%s'", name)
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
    "ReportService",
]
