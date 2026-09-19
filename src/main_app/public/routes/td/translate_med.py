"""
Defines the main routes for the application, such as the homepage.
"""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    request,
)

from ....database.services import InProcessService
from ....services.auth import get_current_user

logger = logging.getLogger(__name__)


class TranslateRoutes:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self.in_process_service = InProcessService()
        self._setup_routes()

    def _setup_routes(self) -> None:

        routes = [
            ("/", "GET", self.index),
        ]
        for rule, method, target in routes:
            self.bp.route(rule, methods=[method])(target)

    def index(self) -> str:
        """ """
        user = get_current_user()
        if user is None:
            return "Not logged in"

        langcode = request.args.get("langcode", type=str)
        # camp = request.args.get("camp", type=str)
        word = request.args.get("word", type=int)
        cat = request.args.get("cat", type=str)
        tra_type = request.args.get("tra_type", type=str)
        title = request.args.get("title", type=str)

        if not langcode or not cat or not tra_type or not title:
            return "Invalid request"

        record = self.in_process_service.get_in_process_by_title_user_lang(
            title,
            user.username,
            langcode,
        )
        if record is None:
            record = self.in_process_service.add_in_process(
                title=title,
                user=user.username,
                lang=langcode,
                cat=cat,
                translate_type=tra_type,
                word=word,
            )


__all__ = [
    "TranslateRoutes",
]
