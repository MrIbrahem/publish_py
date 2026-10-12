"""Post/Publish endpoint for Content Translation.

Mirrors: php_src/endpoints/post.php

This endpoint handles publishing translated pages to Wikipedia.
"""

from __future__ import annotations

import logging

from flask import Blueprint, Response, jsonify, request
from flask.views import MethodView

from ....services.core.cors import check_cors, validate_access
from .worker import _handle_form

logger = logging.getLogger(__name__)


class PublishPreflightView(MethodView):
    """Answer the CORS preflight request for the publish endpoint."""

    decorators = [check_cors]

    def options(self) -> Response:
        """Handle preflight requests."""
        response = Response("", status=200)
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Secret-Key"
        return response


class PublishIndexView(MethodView):
    """Publish a translated page to the target wiki."""

    decorators = [validate_access]  # Check for `X-Secret-Key` headers

    def post(self) -> Response:
        """
        Handle post/publish requests.

        Request Body (JSON):
            user: Username
            title: Target page title
            target: Target language code
            sourcetitle: Source page title
            summary: Edit summary
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


class PublishRoutes:
    """Registrar for the publish endpoint views."""

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register the preflight and publish endpoints on the blueprint."""
        bp.add_url_rule("/", view_func=PublishPreflightView.as_view("publish_preflight"), methods=["OPTIONS"])
        bp.add_url_rule("/", view_func=PublishIndexView.as_view("index"), methods=["POST"])

        # Legacy support for old endpoint path
        bp.add_url_rule(
            "/index.php", view_func=PublishPreflightView.as_view("publish_preflight_old"), methods=["OPTIONS"]
        )
        bp.add_url_rule("/index.php", view_func=PublishIndexView.as_view("index_old"), methods=["POST"])


__all__ = [
    "PublishRoutes",
]
