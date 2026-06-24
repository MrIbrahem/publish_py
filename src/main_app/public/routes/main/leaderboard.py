"""
Defines the main routes for the application, such as the homepage.
"""

from __future__ import annotations

import logging

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
    top_lang_of_users,
)

bp_leaderboard = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")
logger = logging.getLogger(__name__)


@bp_leaderboard.get("/")
def index() -> str:
    year = request.args.get("year", type=int)
    # month = request.args.get("month", type=int)
    camp = request.args.get("camp", type=str)
    user_group = request.args.get("user_group", type=str)

    campaign_to_cats = get_camp_to_cats()
    campaigns = campaign_to_cats.keys()
    years: list[int] = get_pages_years()
    months: list[int] = get_months_of_pages_years(year) if year else []
    user_groups = [x.g_title for x in list_projects()]

    cat = campaign_to_cats.get(camp) if camp and camp != "all" else None

    chart_data = get_chart_data_formatted(
        camp=camp if camp != "all" else None,
        cat=cat,
        user_group=user_group if user_group != "all" else None,
        year=year,
        # month=month, # dont filter chart by month
    )

    form_selected_data = request.args
    form_data = {
        "campaigns": campaigns,
        "years": years,
        "months": months,
        "user_groups": user_groups,
    }

    pages_rows = []

    return render_template(
        "leaderboard/index.html",
        # data to use in form
        form_data=form_data,
        selected_data=form_selected_data,
        chart_data=chart_data,
        # main data
        pages=pages_rows,
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

    chart_data = get_chart_data_formatted(
        lang=lang_code,
        year=selected_year,
    )

    return render_template(
        "leaderboard/langs.html",
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
        # main data
        pages=lang_pages,
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
        "leaderboard/users.html",
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
        # main data
        pages=user_pages,
    )


__all__ = [
    "bp_leaderboard",
]
