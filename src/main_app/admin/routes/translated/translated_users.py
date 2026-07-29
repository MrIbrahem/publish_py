"""
Admin routes for translated user pages (``pages_users`` table).
"""

from __future__ import annotations

import logging

from flask import Blueprint

from .translated_shared_routes import SharedTranslatedRoutes

# from ...db.services import UserPagesService

logger = logging.getLogger(__name__)


class TranslatedUsersRoutes(SharedTranslatedRoutes):
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        super().__init__(
            service_name="pages_users",
            endpoint_name="translated_users",
            table_label="User",
        )
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["GET"])(self.index)
        self.bp.route("/edit", methods=["GET"])(self.edit)
        self.bp.route("/edit", methods=["POST"])(self.edit_post)


__all__ = [
    "TranslatedUsersRoutes",
]
