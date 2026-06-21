"""
Defines the main routes for the application, such as the homepage.
"""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    render_template,
    request,
    send_from_directory,
)

from ....db.services import get_camp_to_cats, list_projects
from ....db.services.pages import (
    get_leaderboard_chart_data,
    get_months_of_pages_years,
    get_pages,
    get_pages_years,
    top_lang_of_users,
)

bp_leaderboard = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")
logger = logging.getLogger(__name__)


@bp_leaderboard.get("/")
def index() -> str:
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    camp = request.args.get("camp", type=str)
    user_group = request.args.get("user_group", type=str)

    campaign_to_cats = get_camp_to_cats()
    campaigns = campaign_to_cats.keys()
    years: list[int] = get_pages_years()
    months: list[int] = get_months_of_pages_years(year) if year else []
    user_groups = [x.g_title for x in list_projects()]

    cat = campaign_to_cats.get(camp) if camp and camp != "all" else None
    chart_data_raw = get_leaderboard_chart_data(
        camp=camp if camp != "all" else None,
        cat=cat,
        user_group=user_group if user_group != "all" else None,
        year=year,
        month=month,
    )
    chart_labels = [row["date"] for row in chart_data_raw]
    chart_counts = [row["count"] for row in chart_data_raw]

    form_data = request.args
    return render_template(
        "leaderboard/index.html",
        campaigns=campaigns,
        years=years,
        months=months,
        user_groups=user_groups,
        form=form_data,
        chart_labels=chart_labels,
        chart_counts=chart_counts,
    )


@bp_leaderboard.get("/langs/<string:lang_code>")
def langs(lang_code: str) -> str:
    selected_year = request.args.get("year", type=int)
    lang_years: list[int] = get_pages_years(lang=lang_code)

    lang_pages = get_pages(
        year=selected_year,
        lang=lang_code,
    )

    words_total = sum(int(page["word"]) for page in lang_pages if page.get("word"))
    pageviews_total = sum(int(page["views"]) for page in lang_pages if page.get("views"))

    chart_data_raw = get_leaderboard_chart_data(
        lang=lang_code,
        year=selected_year,
    )
    chart_labels = [row["date"] for row in chart_data_raw]
    chart_counts = [row["count"] for row in chart_data_raw]

    return render_template(
        "leaderboard/langs.html",
        lang_code=lang_code,
        pages=lang_pages,
        selected_year=selected_year,
        years=lang_years,
        words_total=words_total,
        pageviews_total=pageviews_total,
        chart_labels=chart_labels,
        chart_counts=chart_counts,
    )


@bp_leaderboard.get("/users/<string:username>")
def users(username: str) -> str:
    selected_year = request.args.get("year", type=int)
    selected_lang = request.args.get("lang", type=str)

    user_years: list[int] = get_pages_years(user=username)
    user_langs = top_lang_of_users(username)

    user_pages = get_pages(
        user=username,
        year=selected_year,
        lang=selected_lang,
    )
    words_total = sum(page["word"] for page in user_pages if page.get("word"))
    pageviews_total = sum(page["views"] for page in user_pages if page.get("views"))

    chart_data_raw = get_leaderboard_chart_data(
        user=username,
        year=selected_year,
        lang=selected_lang,
    )
    chart_labels = [row["date"] for row in chart_data_raw]
    chart_counts = [row["count"] for row in chart_data_raw]

    return render_template(
        "leaderboard/users.html",
        username=username,
        pages=user_pages,
        years=user_years,
        langs=user_langs,
        selected_lang=selected_lang,
        selected_year=selected_year,
        words_total=words_total,
        pageviews_total=pageviews_total,
        chart_labels=chart_labels,
        chart_counts=chart_counts,
    )


@bp_leaderboard.get("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/x-icon")


__all__ = ["bp_leaderboard"]
