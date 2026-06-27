"""
SQLAlchemy-based service for managing QIDs.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy import text

from ....extensions import db

logger = logging.getLogger(__name__)


def list_targets_by_lang(lang: str) -> List[dict]:
    """ """
    sql = text(
        """
		SELECT
			t.qid AS qid,
			q.title AS title,
			MIN(aa.category) AS category,
			t.code AS code,
			t.target AS target
		FROM
			qids q
			JOIN all_qids_exists t ON t.qid = q.qid
			LEFT JOIN category_members aa ON aa.article_id = q.title
		WHERE
			t.code = ?
			AND t.target != ''
			AND t.target IS NOT NULL
		GROUP BY
			t.qid, q.title, t.code, t.target
    """
    )
    rows = db.session.execute(sql, {"lang": lang}).fetchall()
    return [dict(row._mapping) for row in rows]


__all__ = [
    "list_targets_by_lang",
]
