""" """

from __future__ import annotations

import logging

from flask import Blueprint, Flask
from flask_wtf.csrf import CSRFProtect

logger = logging.getLogger(__name__)

# CSRF Protection
csrf = CSRFProtect()


def csrf_init_app(app: Flask) -> None:
    """Initialize CSRF protection."""
    csrf.init_app(app)


def csrf_exempt(app: Flask, bp_publish: Blueprint) -> None:
    """Exempt a blueprint from CSRF protection."""
    if app.config.get("WTF_CSRF_ENABLED"):
        csrf.exempt(bp_publish)


__all__ = [
    "csrf",
    "csrf_init_app",
    "csrf_exempt",
]
