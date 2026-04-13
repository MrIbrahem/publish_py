"""Post/Publish endpoint for Content Translation.

Mirrors: php_src/endpoints/post.php

This endpoint handles publishing translated pages to Wikipedia.
"""

import logging

from flask import Blueprint, Response, jsonify, request

from ...helpers.cors import is_allowed
from ...helpers.format import format_title, format_user
from ...users.store import get_user_token_by_username

from .worker import _process_edit, _handle_no_access

bp_publish = Blueprint("publish", __name__, url_prefix="/publish")
logger = logging.getLogger(__name__)


@bp_publish.route("/", methods=["OPTIONS"])
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
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"

    return response


@bp_publish.route("/", methods=["POST"])
def index() -> Response:
    """Handle post/publish requests.

    Request Body (JSON):
        user: Username
        title: Target page title
        target: Target language code
        sourcetitle: Source page title
        text: Page content
        revid: Source revision ID (optional)
        campaign: Campaign name (optional)
        wpCaptchaId: Captcha ID (optional)
        wpCaptchaWord: Captcha answer (optional)

    Returns:
        JSON response with edit result
    """
    # Check CORS
    allowed = is_allowed()

    if not allowed:
        return jsonify({"error": "Access denied. Requests are only allowed from authorized domains."}), 403

    # Get request data
    request_data = request.get_json() or {}

    # Format inputs
    user = format_user(request_data.get("user", ""))
    title = format_title(request_data.get("title", ""))
    text = request_data.get("text", "")

    # Build operation metadata
    tab = {
        "title": title,
        "summary": "",
        "lang": request_data.get("target", ""),
        "user": user,
        "campaign": request_data.get("campaign", ""),
        "result": "",
        "edit": {},
        "sourcetitle": request_data.get("sourcetitle", ""),
        "request_revid": request_data.get("revid", "") or request_data.get("revision", ""),
        "tr_type": request_data.get("tr_type", "lead"),
        "words": 0,
    }

    # Get access credentials
    user_token = get_user_token_by_username(user)

    if user_token is None:
        response = jsonify(_handle_no_access(tab))
        response.status_code = 403
        response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"
        return response

    # Get credentials
    access_key, access_secret = user_token.decrypted()

    # Add captcha parameters if present
    if request_data.get("wpCaptchaId") and request_data.get("wpCaptchaWord"):
        tab["wp_captcha_params"] = {
            "wpCaptchaId": request_data["wpCaptchaId"],
            "wpCaptchaWord": request_data["wpCaptchaWord"],
        }

    # Process the edit
    editit = _process_edit(access_key, access_secret, text, tab)

    response = jsonify(editit)
    response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"
    return response


__all__ = ["bp_publish"]
