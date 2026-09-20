""" """

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import case, cast
from sqlalchemy.orm.query import Query

from ....extensions import db
from ....public.routes.api.form_utils import ApiFormData
from ...models import (
    CategoryRecord,
    LangRecord,
    PageRecord,
    UserRecord,
    ViewsNewAllRecord,
    WordRecord,
)

logger = logging.getLogger(__name__)


class TopStatsService:

    @staticmethod
    def apply_filters(form: ApiFormData, query: Query) -> Query:
        if form.cat:
            query = query.filter(PageRecord.cat == form.cat)
        elif form.camp:
            query = query.join(
                CategoryRecord,
                (PageRecord.cat == CategoryRecord.category) & (CategoryRecord.campaign == form.camp),
            )

        if form.user_group:
            query = query.join(
                UserRecord,
                (PageRecord.user == UserRecord.username) & (UserRecord.user_group == form.user_group),
            )

        if form.year:
            str_like = f"{form.year}-%"
            if form.month:
                str_like = f"{form.year}-{form.month:02d}%"
            query = query.filter(PageRecord.pupdate.like(str_like))

        return query

    def query_top_users(self, form: ApiFormData) -> list[Any]:
        """
        Query:
            SELECT
                p.user,
                COUNT(p.target) AS targets,
                SUM(
                    CASE
                        WHEN p.word IS NOT NULL
                        AND p.word != 0
                        AND p.word != '' THEN p.word
                        WHEN translate_type = 'all' THEN w.w_all_words
                        ELSE w.w_lead_words
                    END
                ) AS words,
                SUM(
                    CASE
                        WHEN v.views IS NULL
                        OR v.views = '' THEN 0
                        ELSE CAST(v.views AS UNSIGNED)
                    END
                ) AS views
            FROM
                pages p
                LEFT JOIN users u ON p.user = u.username
                LEFT JOIN words w ON w.w_title = p.title
                LEFT JOIN views_new_all v ON p.target = v.target
                AND p.lang = v.lang
                LEFT JOIN langs la ON p.lang = la.code
            WHERE
                p.target != ''
                AND p.target IS NOT NULL
                AND p.user != ''
                AND p.user IS NOT NULL
                AND p.lang != ''
                AND p.lang IS NOT NULL
                AND YEAR (p.pupdate) = '2025'
                AND MONTH (p.pupdate) = '02'
                AND u.user_group = 'WIKI'
                AND p.cat = 'RTT'
            GROUP BY
                p.user
            ORDER BY
                2 DESC
        """
        # Build the word count expression
        word_expr = case(
            (
                PageRecord.word.is_not(None) & (PageRecord.word != 0) & (PageRecord.word != ""),
                PageRecord.word,
            ),
            (PageRecord.translate_type == "all", WordRecord.w_all_words),
            else_=WordRecord.w_lead_words,
        )

        # Build the views expression (CAST to UNSIGNED)
        views_expr = case(
            (ViewsNewAllRecord.views.is_(None) | (ViewsNewAllRecord.views == ""), 0),
            else_=cast(ViewsNewAllRecord.views, db.Integer),
        )

        # Query with joins
        query = (
            db.session.query(
                PageRecord.user,
                db.func.count(PageRecord.target).label("targets"),
                db.func.sum(word_expr).label("words"),
                db.func.sum(views_expr).label("views"),
            )
            .outerjoin(WordRecord, WordRecord.w_title == PageRecord.title)
            .outerjoin(
                ViewsNewAllRecord,
                (PageRecord.target == ViewsNewAllRecord.target) & (PageRecord.lang == ViewsNewAllRecord.lang),
            )
            .filter(PageRecord.target != "")
            .filter(PageRecord.target.is_not(None))
            .filter(PageRecord.user != "")
            .filter(PageRecord.user.is_not(None))
            .filter(PageRecord.lang != "")
            .filter(PageRecord.lang.is_not(None))
        )

        query = self.apply_filters(form, query)

        query = query.group_by(PageRecord.user).order_by(db.func.count(PageRecord.target).desc())

        if form.limit:
            query = query.limit(int(form.limit))
        results = query.all()

        return results

    def query_top_langs(self, form: ApiFormData):
        """
        Query:
            SELECT
                p.lang,
                la.name as lang_name,
                COUNT(p.target) AS targets,
                SUM(
                    CASE
                        WHEN p.word IS NOT NULL
                        AND p.word != 0
                        AND p.word != '' THEN p.word
                        WHEN translate_type = 'all' THEN w.w_all_words
                        ELSE w.w_lead_words
                    END
                ) AS words,
                SUM(
                    CASE
                        WHEN v.views IS NULL
                        OR v.views = '' THEN 0
                        ELSE CAST(v.views AS UNSIGNED)
                    END
                ) AS views
            FROM
                pages p
                LEFT JOIN users u ON p.user = u.username
                LEFT JOIN words w ON w.w_title = p.title
                LEFT JOIN views_new_all v ON p.target = v.target
                AND p.lang = v.lang
                LEFT JOIN langs la ON p.lang = la.code
            WHERE
                p.target != ''
                AND p.target IS NOT NULL
                AND p.user != ''
                AND p.user IS NOT NULL
                AND p.lang != ''
                AND p.lang IS NOT NULL
                AND YEAR (p.pupdate) = '2025'
                AND MONTH (p.pupdate) = '02'
                AND u.user_group = 'WIKI'
                AND p.cat = 'RTT'
            GROUP BY
                p.lang
            ORDER BY
                2 DESC
        """
        # TODO: Move database query to service layer like LeaderboardService or TopStatsService

        # Build the word count expression
        word_expr = case(
            (
                PageRecord.word.is_not(None) & (PageRecord.word != 0) & (PageRecord.word != ""),
                PageRecord.word,
            ),
            (PageRecord.translate_type == "all", WordRecord.w_all_words),
            else_=WordRecord.w_lead_words,
        )

        # Build the views expression (CAST to UNSIGNED)
        views_expr = case(
            (ViewsNewAllRecord.views.is_(None) | (ViewsNewAllRecord.views == ""), 0),
            else_=cast(ViewsNewAllRecord.views, db.Integer),
        )

        # Query with joins
        query = (
            db.session.query(
                PageRecord.lang,
                LangRecord.name.label("lang_name"),
                db.func.count(PageRecord.target).label("targets"),
                db.func.sum(word_expr).label("words"),
                db.func.sum(views_expr).label("views"),
            )
            .outerjoin(WordRecord, WordRecord.w_title == PageRecord.title)
            .outerjoin(
                ViewsNewAllRecord,
                (PageRecord.target == ViewsNewAllRecord.target) & (PageRecord.lang == ViewsNewAllRecord.lang),
            )
            .outerjoin(LangRecord, PageRecord.lang == LangRecord.code)
            .filter(PageRecord.target != "")
            .filter(PageRecord.target.is_not(None))
            .filter(PageRecord.user != "")
            .filter(PageRecord.user.is_not(None))
            .filter(PageRecord.lang != "")
            .filter(PageRecord.lang.is_not(None))
        )

        query = self.apply_filters(form, query)
        query = query.group_by(PageRecord.lang, LangRecord.name).order_by(db.func.count(PageRecord.target).desc())
        if form.limit:
            query = query.limit(int(form.limit))

        results = query.all()

        return results


__all__ = [
    "TopStatsService",
]
