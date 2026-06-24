"""
SQLAlchemy-based service helpers for leaderboard page statistics.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, text

from ....shared.core.extensions import db
from ...models import CategoryRecord, PageRecord, UserRecord


def get_pages_years(
    user: str | None = None,
    lang: str | None = None,
) -> list[int]:
    """
    SELECT DISTINCT YEAR(pupdate) AS year FROM pages WHERE pupdate <> ''
    """
    query = db.session.query(func.year(PageRecord.pupdate).label("year")).filter(PageRecord.pupdate != "")
    if user is not None:
        query = query.filter(PageRecord.user == user)

    if lang is not None:
        query = query.filter(PageRecord.lang == lang)

    rows = query.distinct().all()
    years: list[int] = [row.year for row in rows if row.year is not None]
    years.sort(reverse=True)
    return years


def get_months_of_pages_years(year: int) -> list[int]:
    """
    SELECT DISTINCT MONTH(pupdate) AS month FROM pages
    WHERE pupdate <> ''
    AND YEAR(pupdate) = :year
    """
    rows = (
        db.session.query(
            func.month(PageRecord.pupdate).label("month"),
        )
        .filter(PageRecord.pupdate != "")
        .filter(func.year(PageRecord.pupdate) == year)
        .distinct()
        .all()
    )
    months: list[int] = [row.month for row in rows if row.month is not None]
    months.sort(reverse=True)
    return months


def list_of_users_by_translations_count() -> dict[str, int]:
    """
    Get a dictionary of users and their translation counts.

    Returns:
        Dictionary mapping username to count of published translations,
        ordered by count descending.
    """
    result: dict[str, int] = {}
    # Query: SELECT user, COUNT(target) as count FROM pages WHERE target != '' GROUP BY user ORDER BY count DESC
    rows = (
        db.session.query(PageRecord.user, func.count(PageRecord.target).label("count"))
        .filter(PageRecord.target != "")
        .filter(PageRecord.target.isnot(None))
        .group_by(PageRecord.user)
        .order_by(db.func.count(PageRecord.target).desc())
        .all()
    )
    for user, count in rows:
        if user is not None:
            result[user] = count
    return result


def get_pages(
    year: int | None = None,
    user: str | None = None,
    lang: str | None = None,
) -> list[dict]:
    """
    Return pages with views, optionally filtered by year, user, and language.

    SELECT DISTINCT
        p.title, p.word, p.translate_type, p.cat, p.lang,
        p.user, p.target, p.date, p.pupdate, p.add_date, p.deleted,
        v.views
    FROM pages p
    LEFT JOIN views_new_all v ON p.target = v.target AND p.lang = v.lang
    [WHERE conditions by year/user/lang]
    """
    conditions: list[str] = []
    params: dict[str, object] = {}

    if lang is not None:
        conditions.append("p.lang = :lang")
        params["lang"] = lang
    if user is not None:
        conditions.append("p.user = :user")
        params["user"] = user
    if year is not None:
        conditions.append(":year IN (YEAR(p.date), YEAR(p.pupdate), YEAR(p.add_date))")
        params["year"] = year

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    sql = text(
        f"""
        SELECT DISTINCT
            p.title, p.word, p.translate_type, p.cat, p.lang,
            p.user, p.target, p.date, p.pupdate, p.add_date, p.deleted,
            v.views, ca.campaign
        FROM pages p
        LEFT JOIN views_new_all v
            ON p.target = v.target AND p.lang = v.lang
        LEFT JOIN categories ca
            ON ca.category = p.cat
        WHERE {where_clause}
    """
    )

    rows = db.session.execute(sql, params).fetchall()
    return [dict(row._mapping) for row in rows]


def top_lang_of_users(username: str) -> dict[str, int]:
    """
    SELECT
        p.user,
        p.lang,
        COUNT(p.target) AS cnt
    FROM
        pages p
    WHERE
        p.target != ''
        AND p.target IS NOT NULL
        AND p.user IN ('DaSupremo')
    GROUP BY
        p.user,
        p.lang
    result_example: { "user": "DaSupremo", "lang": "gpe", "cnt": 451 }
    """
    data = (
        db.session.query(
            PageRecord.user,
            PageRecord.lang,
            func.count(PageRecord.target).label("cnt"),
        )
        .filter(PageRecord.target != "", PageRecord.target.isnot(None))
        .filter(PageRecord.user == username)
        .group_by(PageRecord.user, PageRecord.lang)
        .order_by(db.func.count(PageRecord.target).desc())
        .all()
    )
    result = {row.lang: row.cnt for row in data}
    return result


def get_leaderboard_chart_data(
    camp: str | None = None,
    cat: str | None = None,
    user_group: str | None = None,
    year: int | None = None,
    month: int | None = None,
    lang: str | None = None,
    user: str | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch aggregated counts of translations by month for the leaderboard chart.
    """
    if db.engine.name == "sqlite":
        date_expr = func.strftime("%Y-%m", PageRecord.pupdate)
    else:
        date_expr = func.left(PageRecord.pupdate, 7)

    query = db.session.query(date_expr.label("date"), func.count().label("count")).filter(
        PageRecord.target.isnot(None), PageRecord.target != ""
    )

    if cat:
        query = query.filter(PageRecord.cat == cat)
    elif camp:
        query = query.join(
            CategoryRecord,
            (PageRecord.cat == CategoryRecord.category) & (CategoryRecord.campaign == camp),
        )

    if user_group:
        query = query.join(
            UserRecord,
            (PageRecord.user == UserRecord.username) & (UserRecord.user_group == user_group),
        )

    if year:
        str_like = f"{year}-%"
        if month:
            str_like = f"{year}-{month:02d}%"
        query = query.filter(PageRecord.pupdate.like(str_like))

    if lang:
        query = query.filter(PageRecord.lang == lang)

    if user:
        query = query.filter(PageRecord.user == user)

    query = query.group_by(date_expr).order_by(date_expr)

    rows = query.all()
    return [{"date": row.date, "count": row.count} for row in rows]


def get_chart_data_formatted(
    camp: str | None = None,
    cat: str | None = None,
    user_group: str | None = None,
    year: int | None = None,
    month: int | None = None,
    lang: str | None = None,
    user: str | None = None,
) -> dict[str, list]:

    chart_data_raw = get_leaderboard_chart_data(
        camp=camp,
        cat=cat,
        user_group=user_group,
        year=year,
        month=month,
        lang=lang,
        user=user,
    )

    chart_labels = [row["date"] for row in chart_data_raw]
    chart_counts = [row["count"] for row in chart_data_raw]
    chart_data = {
        "labels": chart_labels,
        "counts": chart_counts,
    }
    return chart_data


__all__ = [
    "get_pages_years",
    "get_months_of_pages_years",
    "list_of_users_by_translations_count",
    "get_pages",
    "top_lang_of_users",
    "get_leaderboard_chart_data",
    "get_chart_data_formatted",
]
