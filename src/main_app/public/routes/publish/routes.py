"""Post/Publish endpoint for Content Translation.

Mirrors: php_src/endpoints/post.php

This endpoint handles publishing translated pages to Wikipedia.
"""

import logging

from flask import Blueprint, Response, jsonify, request
from marshmallow import ValidationError

from ....db.services.users import UserTokenService
from ....shared.core.cors import check_cors, validate_access
from ....shared.schemas import PublishRequestSchema
from ....shared.utils.helpers.format import format_title, format_user
from .worker import _handle_no_access, _process_edit

logger = logging.getLogger(__name__)


def _handle_form(request_data) -> Response:
    # Validate using marshmallow schema
    raw = {k: v for k, v in request_data.items() if v != "" and str(v).lower() != "all"}

    # translate_type can be "all" - only include if present in request
    translate_type = request_data.get("translate_type", "")
    if translate_type:
        raw["translate_type"] = translate_type

    try:
        validated_data = PublishRequestSchema().load(raw, unknown="exclude")
    except ValidationError as err:
        response = jsonify({"error": {"code": "validation_error", "info": err.messages}})
        response.status_code = 400
        return response

    if validated_data is None:
        response = jsonify({"error": {"code": "validation_error", "info": ""}})
        response.status_code = 400
        return response

    validated_dict = {x: v for x, v in validated_data.items() if v is not None}  # type: ignore

    # Format inputs
    user = format_user(validated_dict.get("user", ""))
    title = format_title(validated_dict.get("title", ""))
    text = validated_dict.get("text", "")

    # Build operation metadata
    tab = {
        "title": title,
        "summary": "",
        "lang": validated_dict.get("target", ""),
        "user": user,
        "campaign": validated_dict.get("campaign", ""),
        "result": "",
        "edit": {},
        "sourcetitle": validated_dict.get("sourcetitle", ""),
        "request_revid": validated_dict.get("revid", "") or validated_dict.get("revision", ""),
        "translate_type": validated_dict.get("translate_type", "lead"),
        "words": 0,
    }

    # Get access credentials
    token_service = UserTokenService()
    user_token = token_service.get_user_token_by_username(user)

    if user_token is None:
        response = jsonify(_handle_no_access(tab))
        response.status_code = 403
        return response

    # Get credentials
    access_key, access_secret = user_token.decrypted()

    # Add captcha parameters if present
    if validated_dict.get("wpCaptchaId") and validated_dict.get("wpCaptchaWord"):
        tab["wp_captcha_params"] = {
            "wpCaptchaId": validated_dict["wpCaptchaId"],
            "wpCaptchaWord": validated_dict["wpCaptchaWord"],
        }

    # Process the edit
    editit = _process_edit(access_key, access_secret, text, tab)

    response = jsonify(editit)
    return response


class PublishRoutes:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["OPTIONS"])(check_cors(self.publish_preflight))
        self.bp.route("/", methods=["POST"])(validate_access(self.index))

    def publish_preflight(self) -> Response:
        response = Response("", status=200)
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Secret-Key"
        return response

    def index(self) -> Response:
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

        return _handle_form(request_data)


__all__ = [
    "PublishRoutes",
]
