"""
Admin routes for translated main pages (``pages`` table).
"""

from __future__ import annotations

import logging

from flask import Blueprint

from .translated_shared_routes import SharedTranslatedRoutes

logger = logging.getLogger(__name__)


class TranslatedRoutes(SharedTranslatedRoutes):
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        super().__init__(
            service_name="pages",
            endpoint_name="translated",
            table_label="Main",
        )
        self._setup_routes()

    def _setup_routes(self) -> None:
        routes = [
            ("/", "GET", self.index),
            ("/edit", "GET", self.edit),
            ("/edit", "POST", self.edit_post),
        ]
        for rule, method, target in routes:
            self.bp.route(rule, methods=[method])(target)


__all__ = [
    "TranslatedRoutes",
]
