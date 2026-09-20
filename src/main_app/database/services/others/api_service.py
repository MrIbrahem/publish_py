"""
API endpoints for API.

Mirrors: php_src/endpoints/index.php?get=publish_reports
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.engine.row import Row

from ....extensions import db
from ...models import CategoryRecord, InProcessRecord, LangRecord, PageRecord, ReportRecord

logger = logging.getLogger(__name__)


class ApiService:
    def get_unique_languages(self) -> list[Row[tuple[str | None]]]:

        results = (
            db.session.query(PageRecord.lang)
            .distinct()
            .outerjoin(CategoryRecord, PageRecord.cat == CategoryRecord.category)
            .filter(PageRecord.lang != "", PageRecord.lang.isnot(None))
            .order_by(PageRecord.lang)
            .all()
        )

        return results

    def get_unique_report_records(self) -> list[Any]:
        results = (
            db.session.query(
                db.func.extract("year", ReportRecord.date).label("year"),
                db.func.extract("month", ReportRecord.date).label("month"),
                ReportRecord.lang,
                ReportRecord.user,
                ReportRecord.result,
            )
            .distinct()
            .all()
        )

        return results

    def fetch_in_process_records(self, lang: str, limit: int) -> list[Any]:
        # Perform the JOIN query using SQLAlchemy
        query = (
            db.session.query(
                InProcessRecord.id,
                InProcessRecord.title,
                InProcessRecord.user,
                InProcessRecord.lang,
                InProcessRecord.cat,
                InProcessRecord.translate_type,
                InProcessRecord.word,
                InProcessRecord.add_date,
                CategoryRecord.campaign.label("campaign"),
                LangRecord.autonym.label("autonym"),
            )
            .outerjoin(CategoryRecord, InProcessRecord.cat == CategoryRecord.category)
            .outerjoin(LangRecord, InProcessRecord.lang == LangRecord.code)
        )

        if lang and lang.lower() != "all":
            query = query.filter(InProcessRecord.lang == lang)

        results = query.order_by(InProcessRecord.id.asc()).limit(limit).all()

        return results


__all__ = [
    "ApiService",
]
