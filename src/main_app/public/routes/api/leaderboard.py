"""
"""

from __future__ import annotations

import logging

from flask import Response, jsonify, request

from ....db.models import CategoryRecord, PageRecord, UserRecord
from ....shared.core.extensions import db
from .form_utils import get_form, FormData

logger = logging.getLogger(__name__)


def leaderboard_status() -> Response:
    """
    Handle leaderboard API requests.
    /api/status?camp=Video&user_group=WIKI&year=2025&month=02&cat=RTTVideo
        SELECT
            LEFT (p.pupdate, 7) as date,
            COUNT(*) as count
        FROM
            pages p
            LEFT JOIN users u ON p.user = u.username
        WHERE
            p.target != ''
            AND YEAR (p.pupdate) = '2025'
            AND u.user_group = 'WIKI'
            AND p.cat = 'RTTVideo'
        GROUP BY
            1
        ORDER BY
            1 ASC;
    """
    query = db.session.query()

    form: FormData = get_form(request.args)
    if form.cat:
        query = query.filter(PageRecord.cat == form.cat)
    elif form.camp:
        query = query.outerjoin(
            CategoryRecord,
            (PageRecord.cat == CategoryRecord.category) & (CategoryRecord.campaign == form.camp),
        )

    if form.user_group:
        query = query.outerjoin(
            UserRecord,
            (PageRecord.user == UserRecord.username) & (UserRecord.user_group == form.user_group),
        )

    if form.year:
        str_like = f"{form.year}-%"
        if form.month:
            str_like = f"{form.year}-{form.month:02d}%"
        query = query.filter(PageRecord.pupdate.like(str_like))

    query = (
        query
        # .group_by()
        # .order_by()
    )
    results = query.all()
    # data example: [ { "date": "2025-02", "count": 1 }, { "date": "2025-04", "count": 3 } ]
    data = {}

    response_data = {
        "results": data,
        "count": len(data),
    }

    response = jsonify(response_data)

    return response

__all__ = [
    "leaderboard_status",
]
