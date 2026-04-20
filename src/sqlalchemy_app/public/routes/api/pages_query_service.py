"""
SQLAlchemy-based service for pages_users and pages_with_views queries.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from ....shared.engine import get_session
from ....shared.models import _CategoryRecord, _PageRecord, _UserPageRecord
from ...models import _ViewsNewAllRecord

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
        results = (
            session.query(
                _UserPageRecord,
                _CategoryRecord.campaign.label("campaign"),
            )
            .outerjoin(_CategoryRecord, _UserPageRecord.cat == _CategoryRecord.category)
            .filter(_UserPageRecord.target != "")
            .filter(_UserPageRecord.target.is_not(None))
            .order_by(_UserPageRecord.pupdate.desc())
            .limit(limit)
            .all()
        )

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
            session.query(_ViewsNewAllRecord.views)
            .filter(_ViewsNewAllRecord.target == _PageRecord.target)
            .filter(_ViewsNewAllRecord.lang == _PageRecord.lang)
            .correlate(_PageRecord)
            .scalar_subquery()
        )

        results = (
            session.query(
                _PageRecord,
                views_subquery.label("views"),
            )
            .filter(_PageRecord.target != "")
            .distinct()
            .limit(limit)
            .all()
        )

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
