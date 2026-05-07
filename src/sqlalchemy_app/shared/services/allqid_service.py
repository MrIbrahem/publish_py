"""
SQLAlchemy-based service for managing QIDs.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError

from ...sqlalchemy_models import AllQidsRecord, QidRecord
from ..engine import get_session

logger = logging.getLogger(__name__)

def list_targets_by_lang(lang: str) -> List[dict]:
    """Replicate all_qids_titles VIEW + JOIN with all_qids_exists.

    Equivalent PHP SQL:
    SELECT a.qid, a.title, a.category, t.code, t.target
    FROM all_qids_titles a JOIN all_qids_exists t ON t.qid = a.qid
    WHERE t.code = ? AND t.target != '' AND t.target IS NOT NULL
    """
    sql = text(
        """
        SELECT qq.qid AS qid, q.title AS title, aa.category AS category,
               t.code AS code, t.target AS target
        FROM all_qids qq
        LEFT JOIN qids q ON qq.qid = q.qid
        LEFT JOIN all_articles aa ON aa.article_id = q.title
        JOIN all_qids_exists t ON t.qid = qq.qid
        WHERE t.code = :lang
          AND t.target != '' AND t.target IS NOT NULL
    """
    )
    with get_session() as session:
        rows = session.execute(sql, {"lang": lang}).fetchall()
        return [dict(row._mapping) for row in rows]


__all__ = [
    "list_targets_by_lang",
]
