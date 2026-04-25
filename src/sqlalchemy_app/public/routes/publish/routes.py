"""Post/Publish endpoint for Content Translation.

Mirrors: php_src/endpoints/post.php

This endpoint handles publishing translated pages to Wikipedia.
"""

import logging

from flask import Blueprint, Response, jsonify, request
from marshmallow import ValidationError

from ....shared.core.cors import check_cors, validate_access
from ....shared.schemas import PublishRequestSchema
from ....shared.services.user_token_service import get_user_token_by_username
from ....shared.utils.helpers.format import format_title, format_user
from .worker import _handle_no_access, _process_edit

bp_publish = Blueprint("publish", __name__, url_prefix="/publish")
logger = logging.getLogger(__name__)


def handle_form(request_data) -> Response:
    # Validate using marshmallow schema
    raw = {k: v for k, v in request_data.items() if v != "" and (str(v).lower() != "all" and k != "translate_type")}
    try:
        validated_data = PublishRequestSchema().load(raw)
    except ValidationError as err:
        response = jsonify({"error": {"code": "validation_error", "info": err.messages}})
        response.status_code = 400
        return response

    # Format inputs
    user = format_user(validated_data.get("user", ""))
    title = format_title(validated_data.get("title", ""))
    text = validated_data.get("text", "")

    # Build operation metadata
    tab = {
        "title": title,
        "summary": "",
        "lang": validated_data.get("target", ""),
        "user": user,
        "campaign": validated_data.get("campaign", ""),
        "result": "",
        "edit": {},
        "sourcetitle": validated_data.get("sourcetitle", ""),
        "request_revid": validated_data.get("revid", "") or validated_data.get("revision", ""),
        "translate_type": validated_data.get("translate_type", "lead"),
        "words": 0,
    }

    # Get access credentials
    user_token = get_user_token_by_username(user)

    if user_token is None:
        response = jsonify(_handle_no_access(tab))
        response.status_code = 403
        return response

    # Get credentials
    access_key, access_secret = user_token.decrypted()

    # Add captcha parameters if present
    if validated_data.get("wpCaptchaId") and validated_data.get("wpCaptchaWord"):
        tab["wp_captcha_params"] = {
            "wpCaptchaId": validated_data["wpCaptchaId"],
            "wpCaptchaWord": validated_data["wpCaptchaWord"],
        }

    # Process the edit
    editit = _process_edit(access_key, access_secret, text, tab)

    response = jsonify(editit)
    return response


@bp_publish.route("/", methods=["OPTIONS"])
@check_cors
def publish_preflight() -> Response:
    response = Response("", status=200)
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Secret-Key"
    return response


@bp_publish.route("/", methods=["POST"])
@validate_access
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

    # Get request data
    request_data = request.form.to_dict()
    if not request_data:
        json_data = request.get_json(silent=True)
        if json_data is None:
            request_data = {}
        elif isinstance(json_data, dict):
            request_data = json_data
        else:
            response = jsonify({"error": {"code": "request_error", "info": "JSON body must be an object"}})
            response.status_code = 400
            return response

    return handle_form(request_data)


__all__ = ["bp_publish"]
