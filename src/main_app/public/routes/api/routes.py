"""
API endpoints for API.

Mirrors: php_src/endpoints/index.php?get=publish_reports
"""

from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint, Response, jsonify, request
from flask.views import MethodView
from marshmallow import ValidationError

from ....database.models import ReportRecord
from ....database.services import (
    ApiService,
    CategoryService,
    InProcessService,
    LangService,
    LeaderboardService,
    PagesQueryService,
    ReportService,
    UsersService,
)
from ....services.core.cors import check_cors
from ....services.schemas import PublishReportsQuerySchema
from ....services.utils.web_utils import parse_select_fields
from ...mapping import ApiFormData
from .top_stats_routes import get_top_langs, get_top_users

logger = logging.getLogger(__name__)


def _handle_options_preflight():
    """Answer the CORS preflight for every API route (blueprint-wide)."""
    if request.method == "OPTIONS":
        response = Response("", status=200)
        requested_method = request.headers.get("Access-Control-Request-Method", "GET")
        response.headers["Access-Control-Allow-Methods"] = f"{requested_method}, OPTIONS"
        # response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Max-Age"] = "7200"
        return response
    return None


class BaseReportApiView(MethodView):
    """Base view for the report API endpoints.

    Holds the services shared by every API route and implements the
    handlers each endpoint view delegates to. ``check_cors`` is applied
    here so every subclass inherits it.
    """

    decorators = [check_cors]

    def __init__(self) -> None:
        self.leaderboard_service = LeaderboardService()
        self.api_service = ApiService()
        self.lang_service = LangService()
        self.pages_query_service = PagesQueryService()
        self.reports_service = ReportService()
        self.category_service = CategoryService()
        self.in_process_service = InProcessService()
        self.users_service = UsersService()

    def leaderboard_status(self) -> tuple[Response, int] | Response:
        """
        Handle leaderboard API requests.
        /api/status?camp=Video&user_group=WIKI&year=2025&month=02&cat=RTTVideo
        """
        form = ApiFormData.from_request(request.args)
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

    def top_langs(self) -> tuple[Response, int] | Response:
        """Handle top_langs API requests."""
        form = ApiFormData.from_request(request.args)
        result = get_top_langs(form)
        data = result.to_json()
        if result.error:
            return jsonify(data), 500

        return jsonify(data)

    def top_users(self) -> tuple[Response, int] | Response:
        """Handle top_users API requests."""
        form = ApiFormData.from_request(request.args)
        result = get_top_users(form)
        data = result.to_json()
        if result.error:
            return jsonify(data), 500

        return jsonify(data)

    def top_lang_of_users(self) -> tuple[Response, int] | Response:
        """Handle top_lang_of_users API requests."""
        try:
            data = self.leaderboard_service.top_lang_of_users()
        except Exception:
            logger.exception("Error fetching top_lang_of_users data")
            return jsonify({"error": "An internal error occurred"}), 500
        return jsonify(data)

    def publish_reports(self) -> tuple[Response, int] | Response:
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
            records: list[ReportRecord] = self.reports_service.query_reports_with_filters(filters, select_fields, limit)

        except Exception:
            logger.exception("Error fetching publish_reports")
            # Return generic error message to avoid exposing internal details
            return jsonify({"error": "An internal error occurred while fetching reports"}), 500

        # Build response
        data = [r.to_json() for r in records] if records else []

        response_data = {
            "results": data,
            "count": len(data),
        }

        response = jsonify(response_data)

        return response

    def publish_reports_stats(self) -> tuple[Response, int] | Response:
        """
        Handle publish_reports_stats API requests.
        Returns stats for populating filter options (year, month, lang, user, result).

        Returns:
            JSON response with distinct filter values
        """
        try:
            # Query distinct year, month, lang, user, result using SQLAlchemy
            results = self.api_service.get_unique_report_records()

        except Exception:
            logger.exception("Error fetching publish_reports_stats")
            return jsonify({"error": "An internal error occurred while fetching stats"}), 500

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

        response_data = {
            "results": data,
            "count": len(data),
        }

        return jsonify(response_data)

    def in_process(self) -> tuple[Response, int] | Response:
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
            results = self.api_service.fetch_in_process_records(lang, limit)

        except Exception:
            logger.exception("Error fetching in_process data")
            return jsonify({"error": "An internal error occurred while fetching in-process data"}), 500

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

        response_data = {
            "results": data,
            "count": len(data),
        }

        return jsonify(response_data)

    def in_process_total(self) -> tuple[Response, int] | Response:
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
            data = self.in_process_service.get_in_process_counts_by_user()

        except Exception:
            logger.exception("Error fetching in_process_total data")
            return jsonify({"error": "An internal error occurred while fetching in-process total data"}), 500

        response_data = {
            "results": data,
            "count": len(data),
        }

        return jsonify(response_data)

    def pages_users(self) -> tuple[Response, int] | Response:
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
            data = self.pages_query_service.list_pages_users(limit=100)
        except Exception:
            logger.exception("Error fetching pages_users data")
            return jsonify({"error": "An internal error occurred while fetching pages_users data"}), 500

        response_data = {
            "results": data,
            "count": len(data),
        }

        return jsonify(response_data)

    def pages_with_views(self) -> tuple[Response, int] | Response:
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
            data = self.pages_query_service.list_pages_with_views()
        except Exception:
            logger.exception("Error fetching pages_with_views data")
            return jsonify({"error": "An internal error occurred while fetching pages_with_views data"}), 500

        response_data = {
            "results": data,
            "count": len(data),
        }

        return jsonify(response_data)

    def categories(self) -> tuple[Response, int] | Response:
        """
        Handle categories API requests. Returns all category records.
        """
        try:
            records = self.category_service.list_categories()
        except Exception:
            logger.exception("Error fetching categories data")
            return jsonify({"error": "An internal error occurred while fetching categories data"}), 500

        records = [x.to_json() for x in records]
        response_data = {
            "results": records,
            "count": len(records),
        }

        return jsonify(response_data)

    def distinct_langs(self) -> tuple[Response, int] | Response:
        """
        Return distinct languages from pages joined with categories.

        SELECT DISTINCT lang FROM pages p
        LEFT JOIN categories ca ON p.cat = ca.category
        WHERE (p.lang != '' AND p.lang IS NOT NULL)
        """
        try:
            results = self.api_service.get_unique_languages()
            data = [{"lang": row.lang} for row in results]
        except Exception:
            logger.exception("Error fetching distinct langs data")
            return jsonify({"error": "An internal error occurred while fetching distinct langs data"}), 500

        return jsonify({"results": data, "count": len(data)})

    def users_by_translations_count(self) -> tuple[Response, int] | Response:
        """Handle users_by_translations_count API requests."""
        try:
            data = self.leaderboard_service.list_of_users_by_translations_count()
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

    def langs(self) -> tuple[Response, int] | Response:
        """
        Handle langs API requests. Returns all language records.
        """
        try:
            records = self.lang_service.list_langs()
        except Exception:
            logger.exception("Error fetching langs data")
            return jsonify({"error": "An internal error occurred while fetching langs data"}), 500

        records = [x.to_json() for x in records]
        response_data = {
            "results": records,
            "count": len(records),
        }

        return jsonify(response_data)

    def users(self) -> tuple[Response, int] | Response:
        """
        Handle users API requests. Returns all users names.
        """
        userlike = request.args.get("userlike", type=str)
        if not userlike:
            return jsonify({"error": "Query parameter 'userlike' is required"}), 400

        try:
            records = self.users_service.users_search(userlike)
        except Exception:
            logger.exception("Error fetching users data")
            return jsonify({"error": "An internal error occurred while fetching users data"}), 500

        records = [{"username": x} for x in records]

        response_data = {
            "results": records,
            "count": len(records),
        }

        return jsonify(response_data)


class ApiStatusView(BaseReportApiView):
    """Leaderboard status endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return the leaderboard chart data for the given filters."""
        return self.leaderboard_status()


class ApiTopLangsView(BaseReportApiView):
    """Top languages endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return the top languages for the given filters."""
        return self.top_langs()


class ApiTopUsersView(BaseReportApiView):
    """Top users endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return the top users for the given filters."""
        return self.top_users()


class ApiTopLangOfUsersView(BaseReportApiView):
    """Top language per user endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return the top language of every user."""
        return self.top_lang_of_users()


class ApiPublishReportsView(BaseReportApiView):
    """Publish reports endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return the report records matching the query filters."""
        return self.publish_reports()


class ApiPublishReportsStatsView(BaseReportApiView):
    """Publish reports stats endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return the distinct filter values used by the reports UI."""
        return self.publish_reports_stats()


class ApiInProcessView(BaseReportApiView):
    """In-process translations endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return the in-process translation records."""
        return self.in_process()


class ApiInProcessTotalView(BaseReportApiView):
    """In-process totals per user endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return the per-user in-process counts."""
        return self.in_process_total()


class ApiPagesUsersView(BaseReportApiView):
    """pages_users records endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return the latest published userspace pages."""
        return self.pages_users()


class ApiPagesWithViewsView(BaseReportApiView):
    """Pages with pageviews endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return the published pages together with their pageviews."""
        return self.pages_with_views()


class ApiCategoriesView(BaseReportApiView):
    """Categories endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return every category record."""
        return self.categories()


class ApiDistinctLangsView(BaseReportApiView):
    """Distinct languages endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return the distinct languages present in published pages."""
        return self.distinct_langs()


class ApiUsersByTranslationsCountView(BaseReportApiView):
    """Users ranked by translations count endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return every user keyed by their translation count."""
        return self.users_by_translations_count()


class ApiLangsView(BaseReportApiView):
    """Languages endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return every language record."""
        return self.langs()


class ApiUsersView(BaseReportApiView):
    """Users search endpoint."""

    def get(self) -> tuple[Response, int] | Response:
        """Return the users matching the ``userlike`` query parameter."""
        return self.users()


class ApiRoutes:
    """Registrar wiring the report API MethodViews onto a blueprint.

    Endpoint names mirror the legacy handler method names so existing
    ``url_for('api.get_distinct_langs')`` / ``url_for('api.get_users')``
    calls keep resolving.
    """

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register the preflight hook and every API endpoint."""
        bp.before_request(_handle_options_preflight)

        bp.add_url_rule("/status", view_func=ApiStatusView.as_view("leaderboard_status"), methods=["GET"])
        bp.add_url_rule("/top_langs", view_func=ApiTopLangsView.as_view("get_top_langs"), methods=["GET"])
        bp.add_url_rule("/top_users", view_func=ApiTopUsersView.as_view("get_top_users"), methods=["GET"])
        bp.add_url_rule(
            "/top_lang_of_users", view_func=ApiTopLangOfUsersView.as_view("get_top_lang_of_users"), methods=["GET"]
        )
        bp.add_url_rule(
            "/publish_reports", view_func=ApiPublishReportsView.as_view("get_publish_reports"), methods=["GET"]
        )
        bp.add_url_rule(
            "/publish_reports/stats",
            view_func=ApiPublishReportsStatsView.as_view("publish_reports_stats"),
            methods=["GET"],
        )
        bp.add_url_rule("/in_process", view_func=ApiInProcessView.as_view("get_in_process"), methods=["GET"])
        bp.add_url_rule(
            "/in_process_total", view_func=ApiInProcessTotalView.as_view("get_in_process_total"), methods=["GET"]
        )
        bp.add_url_rule("/pages_users", view_func=ApiPagesUsersView.as_view("get_pages_users"), methods=["GET"])
        bp.add_url_rule(
            "/pages_with_views", view_func=ApiPagesWithViewsView.as_view("get_pages_with_views"), methods=["GET"]
        )
        bp.add_url_rule("/categories", view_func=ApiCategoriesView.as_view("get_categories"), methods=["GET"])
        bp.add_url_rule(
            "/distinct_langs", view_func=ApiDistinctLangsView.as_view("get_distinct_langs"), methods=["GET"]
        )
        bp.add_url_rule(
            "/users_by_translations_count",
            view_func=ApiUsersByTranslationsCountView.as_view("users_by_translations_count"),
            methods=["GET"],
        )
        bp.add_url_rule("/langs", view_func=ApiLangsView.as_view("get_langs"), methods=["GET"])
        bp.add_url_rule("/users", view_func=ApiUsersView.as_view("get_users"), methods=["GET"])


__all__ = [
    "ApiRoutes",
]
