"""API endpoints for publish_reports.

Mirrors: php_src/endpoints/index.php?get=publish_reports
"""

import logging
from typing import Any, Dict, List

from flask import Blueprint, Response, jsonify, request
from sqlalchemy import func, text

from ....shared.core.cors import check_cors
from ....shared.engine import get_session
from ....shared.models import _CategoryRecord, _ReportRecord
from ....public.models import _InProcessRecord, _LangRecord
from ....shared.services.report_service import query_reports_with_filters
from ....shared.utils.web_utils import parse_select_fields

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

    # Extract filter parameters
    filters: Dict[str, Any] = {}
    filter_params = ["year", "month", "title", "user", "lang", "sourcetitle", "result"]

    for param in filter_params:
        value = request.args.get(param)
        if value is not None and value != "":
            filters[param] = value

    # Extract select fields
    select_param = request.args.get("select")
    select_fields = parse_select_fields(select_param)

    # Extract limit
    limit = request.args.get("limit", type=int)

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
                    func.extract("year", _ReportRecord.date).label("year"),
                    func.extract("month", _ReportRecord.date).label("month"),
                    _ReportRecord.lang,
                    _ReportRecord.user,
                    _ReportRecord.result,
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
    try:
        with get_session() as session:
            # Perform the JOIN query using SQLAlchemy
            results = (
                session.query(
                    _InProcessRecord.id,
                    _InProcessRecord.title,
                    _InProcessRecord.user,
                    _InProcessRecord.lang,
                    _InProcessRecord.cat,
                    _InProcessRecord.translate_type,
                    _InProcessRecord.word,
                    _InProcessRecord.add_date,
                    _CategoryRecord.campaign.label("campaign"),
                    _LangRecord.autonym.label("autonym"),
                )
                .outerjoin(_CategoryRecord, _InProcessRecord.cat == _CategoryRecord.category)
                .outerjoin(_LangRecord, _InProcessRecord.lang == _LangRecord.code)
                .order_by(_InProcessRecord.id.asc())
                .all()
            )

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
        with get_session() as session:
            # Query counts grouped by user
            results = (
                session.query(
                    _InProcessRecord.user,
                    func.count(_InProcessRecord.id).label("article_count"),
                )
                .group_by(_InProcessRecord.user)
                .order_by(func.count(_InProcessRecord.id).desc())
                .all()
            )

            # Convert results to list of dicts
            data: List[Dict[str, Any]] = [
                {
                    "user": row.user,
                    "article_count": row.article_count,
                }
                for row in results
            ]

    except Exception:
        logger.exception("Error fetching in_process_total data")
        return jsonify({"error": "An internal error occurred while fetching in-process total data"}), 500

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


__all__ = ["bp_api"]
