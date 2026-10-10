"""Admin route for Translations Categories dashboard."""

from __future__ import annotations

import logging

from flask import render_template

logger = logging.getLogger(__name__)


def categories_dashboard() -> str:
    """Render the translations categories dashboard."""
    return render_template("admins/categories.html")


__all__ = [
    "categories_dashboard",
]
