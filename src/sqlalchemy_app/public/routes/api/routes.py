"""API endpoints for publish_reports.

Mirrors: php_src/endpoints/index.php?get=publish_reports
"""

import logging
from typing import Any, Dict, List

from flask import Blueprint, Response, jsonify, request
from sqlalchemy import func, text

from ....shared.core.cors import check_cors
from ....shared.engine import get_session
from ....shared.schemas import PublishReportsQuerySchema
from ....shared.services.category_service import list_categories
from ....shared.services.in_process_service import get_in_process_counts_by_user
from ....shared.services.lang_service import list_langs
from ....shared.services.page_service import list_of_users_by_translations_count
from ....shared.services.report_service import query_reports_with_filters
from ....shared.utils.web_utils import parse_select_fields
from ....sqlalchemy_models import CategoryRecord, InProcessRecord, LangRecord, ReportRecord
from .pages_query_service import list_pages_users, list_pages_with_views
from .top_stats_routes import get_top_langs, get_top_users

bp_api = Blueprint("api", __name__, url_prefix="/api")
logger = logging.getLogger(__name__)


@bp_api.route("/publish_reports", methods=["OPTIONS"])
@check_cors
def publish_reports_preflight() -> Response:
    """
    Handle preflight requests.

    Returns:
        Preflight response
    """

    response = Response("", status=200)
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Max-Age"] = "7200"
    return response


@bp_api.route("/publish_reports", methods=["GET"])
@check_cors
def get_publish_reports() -> Response:
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
    schema = PublishReportsQuerySchema()
    filters: Dict[str, Any] = {}
    filter_params = ["year", "month", "title", "user", "lang", "sourcetitle", "result"]

    for param in filter_params:
        value = request.args.get(param)
        if value is not None and value != "":
            # Convert to appropriate type
            if param in ["year", "month"]:
                try:
                    filters[param] = int(value)
                except ValueError:
                    return jsonify({"error": f"Invalid {param} value, must be integer"}), 400
            else:
                filters[param] = value

    # Validate filters against schema
    validation_errors = schema.validate(filters)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400

    # Extract select fields
    select_param = request.args.get("select")
    select_fields = parse_select_fields(select_param)

    # Extract and validate limit
    limit_str = request.args.get("limit")
    limit = None
    if limit_str:
        try:
            limit = int(limit_str)
            if limit < 1 or limit > 1000:
                return jsonify({"error": "limit must be between 1 and 1000"}), 400
        except ValueError:
            return jsonify({"error": "limit must be an integer"}), 400

    try:
        # Query database
        records = query_reports_with_filters(filters, select_fields, limit)

    except Exception:
        logger.exception("Error fetching publish_reports")
        # Return generic error message to avoid exposing internal details
        return jsonify({"error": "An internal error occurred while fetching reports"}), 500

    # Build response
    data = [r.to_dict() for r in records]

    response_data = {
        "results": data,
        "count": len(data),
    }

    response = jsonify(response_data)

    return response


@bp_api.route("/publish_reports_stats", methods=["GET"])
@check_cors
def publish_reports_stats() -> Response:
    """
    Handle publish_reports_stats API requests.
    Returns stats for populating filter options (year, month, lang, user, result).

    Returns:
        JSON response with distinct filter values
    """
    try:
        with get_session() as session:
            # Query distinct year, month, lang, user, result using SQLAlchemy
            results = (
                session.query(
                    func.extract("year", ReportRecord.date).label("year"),
                    func.extract("month", ReportRecord.date).label("month"),
                    ReportRecord.lang,
                    ReportRecord.user,
                    ReportRecord.result,
                )
                .distinct()
                .all()
            )

            # Convert results to list of dicts
            data: List[Dict[str, Any]] = [
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


@bp_api.route("/in_process", methods=["GET"])
@check_cors
def get_in_process() -> Response:
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
        with get_session() as session:
            # Perform the JOIN query using SQLAlchemy
            query = (
                session.query(
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

            if lang and lang != "All":
                query = query.filter(InProcessRecord.lang == lang)

            results = query.order_by(InProcessRecord.id.asc()).limit(limit).all()

            # Convert results to list of dicts
            data: List[Dict[str, Any]] = [
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


@bp_api.route("/in_process_total", methods=["GET"])
@check_cors
def get_in_process_total() -> Response:
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
        data = get_in_process_counts_by_user()

    except Exception:
        logger.exception("Error fetching in_process_total data")
        return jsonify({"error": "An internal error occurred while fetching in-process total data"}), 500

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


@bp_api.route("/pages_users", methods=["GET"])
@check_cors
def get_pages_users() -> Response:
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
        data = list_pages_users(limit=100)
    except Exception:
        logger.exception("Error fetching pages_users data")
        return jsonify({"error": "An internal error occurred while fetching pages_users data"}), 500

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


@bp_api.route("/pages_with_views", methods=["GET"])
@check_cors
def get_pages_with_views() -> Response:
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
        data = list_pages_with_views()
    except Exception:
        logger.exception("Error fetching pages_with_views data")
        return jsonify({"error": "An internal error occurred while fetching pages_with_views data"}), 500

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


@bp_api.route("/categories", methods=["GET"])
@check_cors
def get_categories() -> Response:
    """
    Handle categories API requests. Returns all category records.
    """
    try:
        records = list_categories()
    except Exception:
        logger.exception("Error fetching categories data")
        return jsonify({"error": "An internal error occurred while fetching categories data"}), 500

    records = [x.to_dict() for x in records]
    response_data = {
        "results": records,
        "count": len(records),
    }

    return jsonify(response_data)


@bp_api.route("/users_by_translations_count", methods=["GET"])
@check_cors
def users_by_translations_count() -> Response:
    """C
    Handle pages_with_views API requests.
    """
    try:
        data = list_of_users_by_translations_count()
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


@bp_api.route("/langs", methods=["GET"])
@check_cors
def get_langs() -> Response:
    """
    Handle langs API requests. Returns all category records.
    """
    try:
        records = list_langs()
    except Exception:
        logger.exception("Error fetching langs data")
        return jsonify({"error": "An internal error occurred while fetching langs data"}), 500

    records = [x.to_dict() for x in records]
    response_data = {
        "results": records,
        "count": len(records),
    }

    return jsonify(response_data)


# Register top_stats routes
bp_api.route("/top_langs", methods=["GET"])(get_top_langs)
bp_api.route("/top_users", methods=["GET"])(get_top_users)

__all__ = ["bp_api"]
