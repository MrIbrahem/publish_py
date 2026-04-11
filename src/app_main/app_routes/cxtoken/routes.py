"""Content Translation token endpoint.

Mirrors: php_src/endpoints/cxtoken.php

This endpoint provides CSRF tokens for Content Translation operations.
It validates CORS, retrieves user access credentials, and returns tokens.
"""

import logging

from flask import Blueprint, Response, jsonify, request

from ...config import settings
from ...helpers.cors import is_allowed
from ...services.oauth_client import get_cxtoken
from ...users.store import delete_user_token_by_username, get_user_token_by_username
from .cache import store_jwt, get_from_store

bp_cxtoken = Blueprint("cxtoken", __name__, url_prefix="/cxtoken")
logger = logging.getLogger(__name__)


def _format_user(user: str) -> str:
    """Format username, applying special user mappings."""
    user = settings.users.special_users.get(user, user)
    return user.replace("_", " ")


def get_cxtoken_for_user_wiki(wiki, user):

    # Get access credentials from database
    user_token = get_user_token_by_username(user)

    if user_token is None:
        cxtoken = {"error": {"code": "no access", "info": "no access"}, "username": user}
        return cxtoken, 403

    # Decrypt credentials
    access_key, access_secret = user_token.decrypted()

    # Get cxtoken
    cxtoken = get_cxtoken(wiki, access_key, access_secret)

    # Handle invalid authorization
    err = cxtoken.get("csrftoken_data", {}).get("error", {}).get("code")
    if err == "mwoauth-invalid-authorization-invalid-user":
        delete_user_token_by_username(user)
        cxtoken = {"error": {"code": "no access", "info": "no access"}, "username": user}
        return cxtoken, 403

    return cxtoken, 200


@bp_cxtoken.route("/", methods=["OPTIONS"])
def index_preflight() -> Response:
    """
    Handle preflight requests.

    Returns:
        Preflight response
    """
    # Check CORS
    allowed = is_allowed()

    # Handle CORS preflight
    if not allowed:
        return jsonify({"error": "CORS not allowed"}), 403

    response = Response("", status=200)
    response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@bp_cxtoken.route("/", methods=["GET"])
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

    if _from_cache := get_from_store(user, wiki):
        cxtoken = _from_cache
        status_code = 200
    else:
        cxtoken, status_code = get_cxtoken_for_user_wiki(wiki, user)

        if status_code == 200:
            store_jwt(cxtoken, user, wiki)

    response = jsonify(cxtoken)
    response.status_code = status_code
    response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"

    return response


__all__ = ["bp_cxtoken"]
