"""
SQLAlchemy-based service for pages_users and pages_with_views queries.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from ....shared.engine import get_session
from ....sqlalchemy_models import CategoryRecord, PageRecord, UserPageRecord, ViewsNewAllRecord

logger = logging.getLogger(__name__)


def list_pages_users(limit: int = 100, lang: str = "") -> List[Dict[str, Any]]:
    """
    Return pages_users records with joined category campaign data.

    Query:
        SELECT title, word, translate_type, cat, lang, user, target, date,
               pupdate, add_date, deleted, mdwiki_revid, campaign
        FROM pages_users p
        LEFT JOIN categories ca ON p.cat = ca.category
        WHERE (target != '' AND target IS NOT NULL)
        ORDER BY pupdate DESC
        LIMIT 100
    """
    with get_session() as session:
        query = (
            session.query(
                UserPageRecord,
                CategoryRecord.campaign.label("campaign"),
            )
            .outerjoin(CategoryRecord, UserPageRecord.cat == CategoryRecord.category)
            .filter(UserPageRecord.target != "")
            .filter(UserPageRecord.target.is_not(None))
        )

        if lang and lang != "All":
            query = query.filter(UserPageRecord.lang == lang)

        results = query.order_by(UserPageRecord.pupdate.desc()).limit(limit).all()

        return [
            {
                **row[0].to_dict(),
                "campaign": row[1] if row[1] else row[0].cat,
            }
            for row in results
        ]


def list_pages_with_views(limit: int = 100, lang: str = "") -> List[Dict[str, Any]]:
    """
    Return pages records with views from views_new_all.

    Query:
        SELECT DISTINCT p.id, p.title, p.word, p.translate_type, p.cat, p.lang,
               p.user, p.target, p.date, p.pupdate, p.add_date, p.deleted,
               p.mdwiki_revid,
               (SELECT v.views FROM views_new_all v
                WHERE p.target = v.target AND p.lang = v.lang) as views
        FROM pages p
        WHERE p.target != ''
    """
    with get_session() as session:
        views_subquery = (
            session.query(ViewsNewAllRecord.views)
            .filter(ViewsNewAllRecord.target == PageRecord.target)
            .filter(ViewsNewAllRecord.lang == PageRecord.lang)
            .correlate(PageRecord)
            .scalar_subquery()
        )

        query = session.query(
            PageRecord,
            views_subquery.label("views"),
        ).filter(PageRecord.target != "")

        if lang and lang != "All":
            query = query.filter(PageRecord.lang == lang)

        results = query.distinct().limit(limit).all()

        return [
            {
                **row[0].to_dict(),
                "views": row[1],
            }
            for row in results
        ]


__all__ = [
    "list_pages_users",
    "list_pages_with_views",
]
