"""
Defines the main routes for the application, such as the homepage.
"""

from __future__ import annotations

import logging
from typing import Any

from flask import (
    Blueprint,
    render_template,
    request,
)

from ....db.services.content import get_camp_to_cats, list_projects
from ....db.services.pages import (
    get_chart_data_formatted,
    get_months_of_pages_years,
    get_pages,
    get_pages_years,
    top_lang_of_user,
    top_lang_of_users,
)
from ..api.top_stats_routes import get_top_langs, get_top_users

logger = logging.getLogger(__name__)


class LeaderBoardRoutes:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/users/<string:username>", methods=["GET"])(self.users)
        self.bp.route("/langs/<string:lang_code>", methods=["GET"])(self.langs)
        self.bp.route("/js", methods=["GET"])(self.index_js)
        self.bp.route("/", methods=["GET"])(self.index)

    def index_js(self) -> str:
        year = request.args.get("year", type=int)
        # month = request.args.get("month", type=int)
        camp = request.args.get("camp", type=str)
        campaign_to_cats = get_camp_to_cats()

        form_data = self.load_form_data(list(campaign_to_cats.keys()), year)

        cat = campaign_to_cats.get(camp) if camp and camp != "all" else None
        chart_data = self.load_chart_data(cat, year, camp)

        numbers_summary = {
            "users": 0,
            "articles": 0,
            "words": 0,
            "languages": 0,
            "pageviews": 0,
        }
        form_selected_data = request.args

        return render_template(
            "td/leaderboard/index-js.html",
            # data to use in form
            form_data=form_data,
            selected_data=form_selected_data,
            chart_data=chart_data,
            numbers_summary=numbers_summary,
        )

    def index(self) -> str:
        year = request.args.get("year", type=int)
        # month = request.args.get("month", type=int)
        camp = request.args.get("camp", type=str)
        campaign_to_cats = get_camp_to_cats()

        form_data = self.load_form_data(list(campaign_to_cats.keys()), year)

        cat = campaign_to_cats.get(camp) if camp and camp != "all" else None
        chart_data = self.load_chart_data(cat, year, camp)

        form_selected_data = request.args

        langs_data = get_top_langs(request.args)
        users_data = get_top_users(request.args)

        result = {
            "langs": langs_data.get("results") or [],
            "users": users_data.get("results") or [],
            "users_top_langs": {},
        }

        if users_data.get("results"):
            # {row["user"]: {"lang": row["lang"], "count": row["count"]} for row in result_list}
            users_top_langs: list[dict[Any, Any]] = top_lang_of_users()
            result["users_top_langs"] = {row["user"]: row for row in users_top_langs}

        users_total = users_data.get("count") or 0
        langs_total = langs_data.get("count") or 0

        numbers_summary = self.load_summary_data(result["users"], users_total, langs_total)

        return render_template(
            "td/leaderboard/index.html",
            # data to use in form
            form_data=form_data,
            selected_data=form_selected_data,
            chart_data=chart_data,
            numbers_summary=numbers_summary,
            result=result,  # main data
        )

    def langs(self, lang_code: str) -> str:
        selected_year = request.args.get("year", type=int)
        lang_years: list[int] = get_pages_years(lang=lang_code)

        lang_pages = get_pages(
            year=selected_year,
            lang=lang_code,
        )

        words_total = sum(int(page["word"]) for page in lang_pages if page.get("word"))
        pageviews_total = sum(int(page["views"]) for page in lang_pages if page.get("views"))

        chart_data = get_chart_data_formatted(
            lang=lang_code,
            year=selected_year,
        )
        return render_template(
            "td/leaderboard/langs.html",
            lang_code=lang_code,
            # data to use in form
            form_data={
                "years": lang_years,
            },
            selected_data={
                "year": selected_year,
            },
            words_total=words_total,
            pageviews_total=pageviews_total,
            chart_data=chart_data,
            pages=lang_pages,  # main data
        )

    def users(self, username: str) -> str:
        selected_year = request.args.get("year", type=int)
        selected_lang = request.args.get("lang", type=str)

        user_years: list[int] = get_pages_years(user=username)
        user_langs = top_lang_of_user(username)

        user_pages = get_pages(
            user=username,
            year=selected_year,
            lang=selected_lang,
        )
        words_total = sum(page["word"] for page in user_pages if page.get("word"))
        pageviews_total = sum(page["views"] for page in user_pages if page.get("views"))

        chart_data = get_chart_data_formatted(
            user=username,
            year=selected_year,
            lang=selected_lang,
        )

        form_data = {
            "years": user_years,
            "langs": user_langs,
        }

        return render_template(
            "td/leaderboard/users.html",
            username=username,
            # data to use in form
            form_data=form_data,
            selected_data={
                "year": selected_year,
                "lang": selected_lang,
            },
            words_total=words_total,
            pageviews_total=pageviews_total,
            chart_data=chart_data,
            pages=user_pages,  # main data
        )

    def load_chart_data(self, cat, year, camp):
        user_group = request.args.get("user_group", type=str)
        chart_data = get_chart_data_formatted(
            camp=camp if camp != "all" else None,
            cat=cat,
            user_group=user_group if user_group != "all" else None,
            year=year,
            # month=month, # dont filter chart by month
        )

        return chart_data

    def load_form_data(self, campaigns: list[str], year: int | None) -> dict[str, Any]:
        years: list[int] = get_pages_years()
        months: list[int] = get_months_of_pages_years(year) if year else []
        user_groups = [x.g_title for x in list_projects()]

        form_data = {
            "campaigns": campaigns,
            "years": years,
            "months": months,
            "user_groups": user_groups,
        }

        return form_data

    def load_summary_data(
        self,
        result_users: list[dict[str, Any]],
        users_total: int,
        langs_total: int,
    ) -> dict[str, int]:
        summary_data = {
            "users": users_total,
            "languages": langs_total,
            "articles": sum(row["targets"] for row in result_users),
            "words": sum(row["words"] for row in result_users),
            "pageviews": sum(row["views"] for row in result_users),
        }
        return summary_data


__all__ = [
    "LeaderBoardRoutes",
]
