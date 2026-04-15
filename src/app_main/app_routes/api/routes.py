"""API endpoints for publish_reports.

Mirrors: php_src/endpoints/index.php?get=publish_reports
"""

import logging
from typing import Any, Dict, List, Optional

from flask import Blueprint, Response, jsonify, request

from ...config import settings
from ....new_app.shared.cors import check_cors
from ...db.db_publish_reports import ReportsDB

bp_api = Blueprint("api", __name__, url_prefix="/api")
logger = logging.getLogger(__name__)


def _parse_select_fields(select_param: Optional[str]) -> Optional[List[str]]:
    """Parse the select parameter into a list of field names."""
    if not select_param:
        return None
    return [f.strip() for f in select_param.split(",") if f.strip()]


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
    select_fields = _parse_select_fields(select_param)

    # Extract limit
    limit = request.args.get("limit", type=int)

    try:
        # Query database
        db = ReportsDB(settings.database_data)
        records = db.query_with_filters(filters, select_fields, limit)

    except Exception as e:
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


__all__ = ["bp_api"]
