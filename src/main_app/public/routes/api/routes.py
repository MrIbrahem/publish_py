"""
API endpoints for API.

Mirrors: php_src/endpoints/index.php?get=publish_reports
"""

from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint, Response, jsonify, request
from marshmallow import ValidationError

from ....database.models import CategoryRecord, InProcessRecord, LangRecord, PageRecord, ReportRecord
from ....database.services import (
    CategoryService,
    InProcessService,
    LangService,
    LeaderboardService,
    PagesQueryService,
    ReportService,
    UsersService,
)
from ....extensions import db
from ....services.core.cors import check_cors
from ....services.schemas import PublishReportsQuerySchema
from ....services.utils.web_utils import parse_select_fields
from .form_utils import FormData, get_form
from .top_stats_routes import get_top_langs, get_top_users

logger = logging.getLogger(__name__)


def get_publish_reports() -> tuple[Response, int] | Response:
    """
    Handle publish_reports API requests.

    Query Parameters:
        year: Filter by year of date
        month: Filter by month of date
        title: Filter by page title
        user: Filter by username
        lang: Filter by language code
        sourcetitle: Filter by source title
        result: Filter by result status
        select: Comma-separated list of fields to return
        limit: Maximum number of results

    Special Values:
        not_empty / not_mt: Field is not empty
        empty / mt: Field is empty
        >0: Field is greater than 0
        all: Skip this filter

    Returns:
        JSON response with matching reports or error
    """

    # Validate query parameters using marshmallow schema
    # Validate & coerce query parameters using marshmallow schema
    raw = {k: v for k, v in request.args.items() if v != "" and str(v).lower() != "all"}
    try:
        validated = PublishReportsQuerySchema().load(raw, unknown="exclude")
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "info": err.messages}), 400

    limit = validated.pop("limit", None)  # type: ignore
    select = validated.pop("select", None)  # type: ignore

    select_fields = parse_select_fields(select)
    filters: dict[str, Any] = validated  # type: ignore

    try:
        # Query database
        service = ReportService()
        records: list[ReportRecord] = service.query_reports_with_filters(filters, select_fields, limit)

    except Exception:
        logger.exception("Error fetching publish_reports")
        # Return generic error message to avoid exposing internal details
        return jsonify({"error": "An internal error occurred while fetching reports"}), 500

    # Build response
    data = [r.to_dict() for r in records] if records else []

    response_data = {
        "results": data,
        "count": len(data),
    }

    response = jsonify(response_data)

    return response


def publish_reports_stats() -> tuple[Response, int] | Response:
    """
    Handle publish_reports_stats API requests.
    Returns stats for populating filter options (year, month, lang, user, result).

    Returns:
        JSON response with distinct filter values
    """
    try:
        # Query distinct year, month, lang, user, result using SQLAlchemy
        results = (
            db.session.query(
                db.func.extract("year", ReportRecord.date).label("year"),
                db.func.extract("month", ReportRecord.date).label("month"),
                ReportRecord.lang,
                ReportRecord.user,
                ReportRecord.result,
            )
            .distinct()
            .all()
        )

        # Convert results to list of dicts
        data: list[dict[str, Any]] = [
            {
                "year": int(row.year) if row.year else None,
                "month": int(row.month) if row.month else None,
                "lang": row.lang,
                "user": row.user,
                "result": row.result,
            }
            for row in results
        ]

    except Exception:
        logger.exception("Error fetching publish_reports_stats")
        return jsonify({"error": "An internal error occurred while fetching stats"}), 500

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


def get_in_process() -> tuple[Response, int] | Response:
    """
    Handle in_process API requests.
    Returns in-process translations with joined category and language data.

    Query:
        SELECT title, user, lang, cat, translate_type, word, add_date,
               ca.campaign, la.autonym
        FROM in_process
        LEFT JOIN categories ca ON cat = ca.category
        LEFT JOIN langs la ON lang = la.code

    Returns:
        JSON response with in-process records
    """
    lang = request.args.get("lang", default="", type=str)
    limit = request.args.get("limit", default=500, type=int)
    limit = max(1, min(limit, 5000))
    try:
        # Perform the JOIN query using SQLAlchemy
        query = (
            db.session.query(
                InProcessRecord.id,
                InProcessRecord.title,
                InProcessRecord.user,
                InProcessRecord.lang,
                InProcessRecord.cat,
                InProcessRecord.translate_type,
                InProcessRecord.word,
                InProcessRecord.add_date,
                CategoryRecord.campaign.label("campaign"),
                LangRecord.autonym.label("autonym"),
            )
            .outerjoin(CategoryRecord, InProcessRecord.cat == CategoryRecord.category)
            .outerjoin(LangRecord, InProcessRecord.lang == LangRecord.code)
        )

        if lang and lang.lower() != "all":
            query = query.filter(InProcessRecord.lang == lang)

        results = query.order_by(InProcessRecord.id.asc()).limit(limit).all()

        # Convert results to list of dicts
        data: list[dict[str, Any]] = [
            {
                "id": row.id,
                "title": row.title,
                "user": row.user,
                "lang": row.lang,
                "cat": row.cat,
                "translate_type": row.translate_type,
                "word": row.word,
                "add_date": row.add_date.isoformat() if row.add_date else None,
                "campaign": row.campaign if row.campaign else row.cat,
                "autonym": row.autonym if row.autonym else row.lang,
            }
            for row in results
        ]

    except Exception:
        logger.exception("Error fetching in_process data")
        return jsonify({"error": "An internal error occurred while fetching in-process data"}), 500

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


def get_in_process_total() -> tuple[Response, int] | Response:
    """
    Handle in_process_total API requests.
    Returns aggregated counts of in-process translations per user.

    Query:
        SELECT user, COUNT(*) as article_count
        FROM in_process
        GROUP BY user
        ORDER BY article_count DESC

    Returns:
        JSON response with user counts
    """
    try:
        service = InProcessService()
        data = service.get_in_process_counts_by_user()

    except Exception:
        logger.exception("Error fetching in_process_total data")
        return jsonify({"error": "An internal error occurred while fetching in-process total data"}), 500

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


def get_pages_users() -> tuple[Response, int] | Response:
    """
    Handle pages_users API requests.
    Returns pages_users records with joined category campaign data.

    Query:
        SELECT title, word, translate_type, cat, lang, user, target, date,
               pupdate, add_date, deleted, mdwiki_revid, campaign
        FROM pages_users p
        LEFT JOIN categories ca ON p.cat = ca.category
        WHERE (target != '' AND target IS NOT NULL)
        ORDER BY pupdate DESC
        LIMIT 100

    Returns:
        JSON response with pages_users records
    """
    try:
        data = PagesQueryService().list_pages_users(limit=100)
    except Exception:
        logger.exception("Error fetching pages_users data")
        return jsonify({"error": "An internal error occurred while fetching pages_users data"}), 500

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


def get_pages_with_views() -> tuple[Response, int] | Response:
    """
    Handle pages_with_views API requests.
    Returns pages records with views from views_new_all.

    Query:
        SELECT DISTINCT p.id, p.title, p.word, p.translate_type, p.cat, p.lang,
               p.user, p.target, p.date, p.pupdate, p.add_date, p.deleted,
               p.mdwiki_revid,
               (SELECT v.views FROM views_new_all v
                WHERE p.target = v.target AND p.lang = v.lang) as views
        FROM pages p
        WHERE p.target != ''

    Returns:
        JSON response with pages records including views
    """
    try:
        data = PagesQueryService().list_pages_with_views()
    except Exception:
        logger.exception("Error fetching pages_with_views data")
        return jsonify({"error": "An internal error occurred while fetching pages_with_views data"}), 500

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


def get_categories() -> tuple[Response, int] | Response:
    """
    Handle categories API requests. Returns all category records.
    """
    try:
        category_service = CategoryService()
        records = category_service.list_categories()
    except Exception:
        logger.exception("Error fetching categories data")
        return jsonify({"error": "An internal error occurred while fetching categories data"}), 500

    records = [x.to_dict() for x in records]
    response_data = {
        "results": records,
        "count": len(records),
    }

    return jsonify(response_data)


def get_distinct_langs() -> tuple[Response, int] | Response:
    """
    Return distinct languages from pages joined with categories.

    SELECT DISTINCT lang FROM pages p
    LEFT JOIN categories ca ON p.cat = ca.category
    WHERE (p.lang != '' AND p.lang IS NOT NULL)
    """
    try:
        results = (
            db.session.query(PageRecord.lang)
            .distinct()
            .outerjoin(CategoryRecord, PageRecord.cat == CategoryRecord.category)
            .filter(PageRecord.lang != "", PageRecord.lang.isnot(None))
            .order_by(PageRecord.lang)
            .all()
        )
        data = [{"lang": row.lang} for row in results]
    except Exception:
        logger.exception("Error fetching distinct langs data")
        return jsonify({"error": "An internal error occurred while fetching distinct langs data"}), 500

    return jsonify({"results": data, "count": len(data)})


def users_by_translations_count() -> tuple[Response, int] | Response:
    """C
    Handle pages_with_views API requests.
    """
    service = LeaderboardService()
    try:
        data = service.list_of_users_by_translations_count()
    except Exception:
        logger.exception("Error fetching list_of_users_by_translations_count data")
        return jsonify({"error": "An internal error occurred while fetching v data"}), 500

    # sort data by value
    data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


def get_langs() -> tuple[Response, int] | Response:
    """
    Handle langs API requests. Returns all language records.
    """
    try:
        lang_service = LangService()
        records = lang_service.list_langs()
    except Exception:
        logger.exception("Error fetching langs data")
        return jsonify({"error": "An internal error occurred while fetching langs data"}), 500

    records = [x.to_dict() for x in records]
    response_data = {
        "results": records,
        "count": len(records),
    }

    return jsonify(response_data)


def get_users() -> tuple[Response, int] | Response:
    """
    Handle users API requests. Returns all users names.
    """
    userlike = request.args.get("userlike", type=str)
    if not userlike:
        return jsonify({"error": "Query parameter 'userlike' is required"}), 400

    try:
        service = UsersService()
        records = service.users_search(userlike)
    except Exception:
        logger.exception("Error fetching users data")
        return jsonify({"error": "An internal error occurred while fetching users data"}), 500

    records = [{"username": x} for x in records]

    response_data = {
        "results": records,
        "count": len(records),
    }

    return jsonify(response_data)


class ApiRoutes:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self.leaderboard_service = LeaderboardService()
        self._setup_routes()

    def _setup_routes(self) -> None:

        self.bp.before_request(self.handle_options_preflight)

        self.bp.route("/status", methods=["GET"])(self.leaderboard_status)
        self.bp.route("/top_langs", methods=["GET"])(check_cors(self.get_top_langs))
        self.bp.route("/top_users", methods=["GET"])(check_cors(self.get_top_users))
        self.bp.route("/top_lang_of_users", methods=["GET"])(check_cors(self.get_top_lang_of_users))
        self.bp.route("/publish_reports", methods=["GET"])(check_cors(get_publish_reports))
        self.bp.route("/publish_reports/stats", methods=["GET"])(check_cors(publish_reports_stats))
        self.bp.route("/in_process", methods=["GET"])(check_cors(get_in_process))
        self.bp.route("/in_process_total", methods=["GET"])(check_cors(get_in_process_total))
        self.bp.route("/pages_users", methods=["GET"])(check_cors(get_pages_users))
        self.bp.route("/pages_with_views", methods=["GET"])(check_cors(get_pages_with_views))
        self.bp.route("/categories", methods=["GET"])(check_cors(get_categories))
        self.bp.route("/distinct_langs", methods=["GET"])(check_cors(get_distinct_langs))
        self.bp.route("/users_by_translations_count", methods=["GET"])(check_cors(users_by_translations_count))
        self.bp.route("/langs", methods=["GET"])(check_cors(get_langs))
        self.bp.route("/users", methods=["GET"])(check_cors(get_users))

    def handle_options_preflight(self):
        if request.method == "OPTIONS":
            response = Response("", status=200)
            requested_method = request.headers.get("Access-Control-Request-Method", "GET")
            response.headers["Access-Control-Allow-Methods"] = f"{requested_method}, OPTIONS"
            # response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Access-Control-Max-Age"] = "7200"
            return response

    def get_top_langs(self) -> tuple[Response, int] | Response:
        result = get_top_langs(request.args)
        data = result.to_json()
        if result.error:
            return jsonify(data), 500

        return jsonify(data)

    def get_top_users(self) -> tuple[Response, int] | Response:
        result = get_top_users(request.args)
        data = result.to_json()
        if result.error:
            return jsonify(data), 500

        return jsonify(data)

    def get_top_lang_of_users(self) -> tuple[Response, int] | Response:
        try:
            data = self.leaderboard_service.top_lang_of_users()
        except Exception:
            logger.exception("Error fetching top_lang_of_users data")
            return jsonify({"error": "An internal error occurred"}), 500
        return jsonify(data)

    def leaderboard_status(self) -> tuple[Response, int] | Response:
        """
        Handle leaderboard API requests.
        /api/status?camp=Video&user_group=WIKI&year=2025&month=02&cat=RTTVideo
        """
        form: FormData = get_form(request.args)
        try:
            data = self.leaderboard_service.get_leaderboard_chart_data(
                camp=form.camp,
                cat=form.cat,
                user_group=form.user_group,
                year=form.year,
                month=form.month,
                lang=form.lang,
                user=form.user,
            )
        except Exception:
            logger.exception("Error fetching leaderboard status data")
            return jsonify({"error": "An internal error occurred"}), 500
        response_data = {
            "results": data,
            "count": len(data),
        }
        return jsonify(response_data)


__all__ = [
    "ApiRoutes",
]
