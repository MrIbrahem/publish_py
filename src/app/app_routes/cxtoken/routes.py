"""Content Translation token endpoint.

Mirrors: php_src/endpoints/cxtoken.php

This endpoint provides CSRF tokens for Content Translation operations.
It validates CORS, retrieves user access credentials, and returns tokens.
"""

import logging

from flask import Blueprint, Response, jsonify, request

from ...helpers.cors import is_allowed
from ...helpers.format import SPECIAL_USERS
from ...services.oauth_client import get_cxtoken
from ...users.store import delete_user_token_by_username, get_user_token_by_username

bp_cxtoken = Blueprint("cxtoken", __name__)
logger = logging.getLogger(__name__)


def _format_user(user: str) -> str:
    """Format username, applying special user mappings."""
    user = SPECIAL_USERS.get(user, user)
    return user.replace("_", " ")


@bp_cxtoken.route("/", methods=["GET", "OPTIONS"])
def index() -> Response:
    """Handle cxtoken requests.

    Query Parameters:
        wiki: Wiki language code (e.g., 'en')
        user: Username

    Returns:
        JSON response with cxtoken data or error
    """
    # Check CORS
    allowed = is_allowed()

    # Handle CORS preflight
    if request.method == "OPTIONS":
        if not allowed:
            return jsonify({"error": "CORS not allowed"}), 403
        response = Response("", status=200)
        response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    if not allowed:
        return jsonify({"error": "Access denied. Requests are only allowed from authorized domains."}), 403

    # Get request parameters
    wiki = request.args.get("wiki", "")
    user = request.args.get("user", "")

    # Validate parameters
    if not wiki or not user:
        return jsonify({"error": {"code": "no data", "info": "wiki or user is empty"}}), 400

    # Format user (apply special user mappings)
    user = _format_user(user)

    # Get access credentials from database
    user_token = get_user_token_by_username(user)

    if user_token is None:
        error_response = {"error": {"code": "no access", "info": "no access"}, "username": user}
        response = jsonify(error_response)
        response.status_code = 403
        response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"
        return response

    # Decrypt credentials
    access_key, access_secret = user_token.decrypted()

    # Get cxtoken
    cxtoken = get_cxtoken(wiki, access_key, access_secret)

    if not cxtoken:
        cxtoken = {"error": "no cxtoken"}

    # Handle invalid authorization
    err = cxtoken.get("csrftoken_data", {}).get("error", {}).get("code")
    if err == "mwoauth-invalid-authorization-invalid-user":
        delete_user_token_by_username(user)
        cxtoken["del_access"] = True

    response = jsonify(cxtoken)
    response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"
    return response


__all__ = ["bp_cxtoken"]
