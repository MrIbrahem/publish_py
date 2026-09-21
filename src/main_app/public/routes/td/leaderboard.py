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
from flask.views import MethodView

from ....database.services import (
    CategoryService,
    InProcessService,
    LeaderboardService,
    ProjectService,
)
from ...mapping import ApiFormData, LeaderBoardData
from ..api.top_stats_routes import get_top_langs, get_top_users
from .leaderboard_mapping import InProcessRow, ReadyRow

logger = logging.getLogger(__name__)


class BaseLeaderBoardView(MethodView):
    """Base view for the leaderboard pages.

    Holds the services shared by every leaderboard page and exposes the
    chart/form/summary builders used by the index views.
    """

    def __init__(self) -> None:
        self.category_service = CategoryService()
        self.project_service = ProjectService()
        self.lederboard_service = LeaderboardService()
        self.inprocess_service = InProcessService()

    def _load_chart_data(
        self,
        cat: str | None,
        year: int | None,
        camp: str | None,
        user_group: str | None,
    ) -> dict[str, list[Any]]:
        """Load the chart series for a campaign/category."""
        chart_data = self.lederboard_service.get_chart_data_formatted(
            camp=camp,
            cat=cat,
            user_group=user_group,
            year=year,
            # month=month, # dont filter chart by month
        )

        return chart_data

    def _load_form_data(self, campaigns: list[str], year: int | None) -> dict[str, Any]:
        """Assemble the filter-form context shared by the index pages."""
        years: list[int] = self.lederboard_service.get_pages_years()
        months: list[int] = self.lederboard_service.get_months_of_pages_years(year) if year else []

        projects = self.project_service.list_projects()
        user_groups = [x.g_title for x in projects]

        form_data = {
            "campaigns": campaigns,
            "years": years,
            "months": months,
            "user_groups": user_groups,
        }

        return form_data

    def _load_summary_data(
        self,
        result_users: list[dict[str, Any]],
        users_total: int,
        langs_total: int,
    ) -> dict[str, int]:
        """Aggregate the top-of-page number summary."""
        summary_data = {
            "users": users_total,
            "languages": langs_total,
            "articles": sum(row["targets"] for row in result_users),
            "words": sum(row["words"] for row in result_users),
            "pageviews": sum(row["views"] for row in result_users),
        }
        return summary_data


class LeaderBoardIndexJsView(BaseLeaderBoardView):
    """Render the JavaScript-driven leaderboard page."""

    def get(self) -> str:
        """Render the JS leaderboard with chart data and an empty summary."""
        args = LeaderBoardData.from_request(request.args)

        campaign_to_cats = self.category_service.get_camp_to_cats()

        form_data = self._load_form_data(list(campaign_to_cats.keys()), args.year)

        cat = campaign_to_cats.get(args.camp) if args.camp else None
        chart_data = self._load_chart_data(cat, args.year, args.camp, args.user_group)

        numbers_summary = {
            "users": 0,
            "articles": 0,
            "words": 0,
            "languages": 0,
            "pageviews": 0,
        }

        return render_template(
            "td/leaderboard/index-js.html",
            # data to use in form
            form_data=form_data,
            selected_data=args,
            chart_data=chart_data,
            numbers_summary=numbers_summary,
        )


class LeaderBoardIndexView(BaseLeaderBoardView):
    """Render the server-rendered leaderboard page."""

    def get(self) -> str:
        """Render the leaderboard with the top languages and users."""
        args = LeaderBoardData.from_request(request.args)

        campaign_to_cats = self.category_service.get_camp_to_cats()

        form_data = self._load_form_data(list(campaign_to_cats.keys()), args.year)

        cat = campaign_to_cats.get(args.camp) if args.camp else None
        chart_data = self._load_chart_data(cat, args.year, args.camp, args.user_group)

        form = ApiFormData.from_request(request.args)
        langs_res = get_top_langs(form)
        users_res = get_top_users(form)

        langs_data = langs_res.to_json()
        users_data = users_res.to_json()

        result = {
            "langs": langs_data["results"] or [],
            "users": users_data["results"] or [],
            "users_top_langs": {},
        }

        if users_data["results"]:
            # {row["user"]: {"lang": row["lang"], "count": row["count"]} for row in result_list}
            users_top_langs: list[dict[Any, Any]] = self.lederboard_service.top_lang_of_users()
            result["users_top_langs"] = {row["user"]: row for row in users_top_langs}

        numbers_summary = self._load_summary_data(result["users"], users_res.count, langs_res.count)

        return render_template(
            "td/leaderboard/index.html",
            # data to use in form
            form_data=form_data,
            selected_data=args,
            chart_data=chart_data,
            numbers_summary=numbers_summary,
            result=result,  # main data
        )


class LeaderBoardLangsView(BaseLeaderBoardView):
    """Render the per-language leaderboard page."""

    def get(self, lang_code: str) -> str:
        """Render the published pages for a single language."""
        args = LeaderBoardData.from_request(request.args)
        lang_years: list[int] = self.lederboard_service.get_pages_years(lang=lang_code)

        lang_pages = self.lederboard_service.get_pages(
            year=args.year,
            lang=lang_code,
        )

        words_total = sum(int(page["word"]) for page in lang_pages if page.get("word"))
        pageviews_total = sum(int(page["views"]) for page in lang_pages if page.get("views"))

        chart_data = self.lederboard_service.get_chart_data_formatted(
            lang=lang_code,
            year=args.year,
        )

        inprocess_pages = []
        if not args.year:
            inprocess_pages = [
                InProcessRow.from_row(x.to_json()) for x in self.inprocess_service.get_lang_in_process(lang=lang_code)
            ]

        lang_pages_items = [ReadyRow.from_row(x) for x in lang_pages]

        return render_template(
            "td/leaderboard/langs.html",
            lang_code=lang_code,
            # data to use in form
            form_data={
                "years": lang_years,
            },
            selected_data=args,
            words_total=words_total,
            pageviews_total=pageviews_total,
            chart_data=chart_data,
            pages=lang_pages_items,  # main data
            inprocess_pages=inprocess_pages,
        )


class LeaderBoardUsersView(BaseLeaderBoardView):
    """Render the per-user leaderboard page."""

    def get(self, username: str) -> str:
        """Render the published pages for a single user."""
        args = LeaderBoardData.from_request(request.args)

        user_years: list[int] = self.lederboard_service.get_pages_years(user=username)
        user_langs = self.lederboard_service.top_lang_of_user(username)

        user_pages = self.lederboard_service.get_pages(
            user=username,
            year=args.year,
            lang=args.lang,
        )
        words_total = sum(page["word"] for page in user_pages if page.get("word"))
        pageviews_total = sum(page["views"] for page in user_pages if page.get("views"))

        chart_data = self.lederboard_service.get_chart_data_formatted(
            user=username,
            year=args.year,
            lang=args.lang,
        )

        form_data = {
            "years": user_years,
            "langs": user_langs,
        }

        inprocess_pages = []
        if not args.year:
            inprocess_pages = [
                InProcessRow.from_row(x.to_json())
                for x in self.inprocess_service.get_user_in_process(user=username)
                if not args.lang or x.lang == args.lang
            ]

        user_pages_items = [ReadyRow.from_row(x) for x in user_pages]

        return render_template(
            "td/leaderboard/users.html",
            username=username,
            # data to use in form
            form_data=form_data,
            selected_data=args,
            words_total=words_total,
            pageviews_total=pageviews_total,
            chart_data=chart_data,
            pages=user_pages_items,  # main data
            inprocess_pages=inprocess_pages,
        )


class LeaderBoardRoutes:
    """Registrar wiring the leaderboard MethodViews onto a blueprint.

    Endpoint names (``users``, ``langs``, ``index_js``, ``index``) are
    preserved from the legacy function-based routes so existing
    ``url_for('leaderboard.index')`` calls keep working.
    """

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register all leaderboard views on the blueprint."""
        bp.add_url_rule("/users/<string:username>", view_func=LeaderBoardUsersView.as_view("users"), methods=["GET"])
        bp.add_url_rule("/langs/<string:lang_code>", view_func=LeaderBoardLangsView.as_view("langs"), methods=["GET"])
        bp.add_url_rule("/js", view_func=LeaderBoardIndexJsView.as_view("index_js"), methods=["GET"])
        bp.add_url_rule("/", view_func=LeaderBoardIndexView.as_view("index"), methods=["GET"])


__all__ = [
    "LeaderBoardRoutes",
]
