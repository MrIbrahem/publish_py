"""Content Translation token endpoint.

Mirrors: php_src/endpoints/cxtoken.php

This endpoint provides CSRF tokens for Content Translation operations.
It validates CORS, retrieves user access credentials, and returns tokens.
"""

import logging

from flask import Blueprint, Response, jsonify, request
from marshmallow import ValidationError

from ....config import settings
from ....database.services import UserTokenService
from ....services.clients.oauth_client import get_cxtoken
from ....services.core.cors import check_cors
from ....services.schemas import CXTokenRequestSchema
from .cache import get_from_store, store_jwt

logger = logging.getLogger(__name__)


def _format_user(user: str) -> str:
    """Format username, applying special user mappings."""
    user = settings.users.special_users.get(user, user)
    return user.replace("_", " ")


def get_cxtoken_for_user_wiki(wiki, user_name):
    # Get access credentials from database
    token_service = UserTokenService()
    user_token = token_service.get_user_token_by_username(user_name)

    if user_token is None:
        cxtoken = {"error": {"code": "no access", "info": "no access"}, "username": user_name}
        return cxtoken, 403

    # Decrypt credentials
    access_key, access_secret = user_token.decrypted()

    # Get cxtoken
    cxtoken = get_cxtoken(wiki, access_key, access_secret)

    if isinstance(cxtoken, str):
        logger.warning("cxtoken error")
        logger.warning(cxtoken)

    # Handle invalid authorization
    err = cxtoken.get("csrftoken_data", {}).get("error", {})
    if err:
        if err.get("code") == "mwoauth-invalid-authorization-invalid-user":
            token_service.delete(user_token.user_id)
            cxtoken = {"error": {"code": "no access", "info": "no access"}, "username": user_name}
            return cxtoken, 403
        else:
            return cxtoken.get("csrftoken_data", {}), 403

    return cxtoken, 200


class CxTokenRoutes:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["OPTIONS"])(check_cors(self.index_preflight))
        self.bp.route("/", methods=["GET"])(check_cors(self.index))

    def index_preflight(self) -> Response:
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

    def index(self) -> Response:
        """Handle cxtoken requests.

        Query Parameters:
            wiki: Wiki language code (e.g., 'en')
            user: Username

        Returns:
            JSON response with cxtoken data or error
        """
        try:
            validated_data = CXTokenRequestSchema().load(request.args, unknown="exclude")
        except ValidationError as err:
            response = jsonify({"error": {"code": "validation_error", "info": err.messages}})
            response.status_code = 400
            return response

        # Get request parameters
        wiki = validated_data.get("wiki", "")  # type: ignore
        user = validated_data.get("user", "")  # type: ignore

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

        return response


__all__ = [
    "CxTokenRoutes",
]
