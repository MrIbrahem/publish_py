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
    form: FormData = get_form(request.args)

    date_expr = db.func.left(PageRecord.pupdate, 7)

    query = db.session.query(date_expr.label("date"), db.func.count().label("count")).filter(
        PageRecord.target != ""
    )

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

    if form.lang:
        query = query.filter(PageRecord.lang == form.lang)

    if form.user:
        query = query.filter(PageRecord.user == form.user)

    query = query.group_by(date_expr).order_by(date_expr)


    rows = query.all()
    data = [{"date": row.date, "count": row.count} for row in rows]

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


__all__ = [
    "leaderboard_status",
]
