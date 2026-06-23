"""
"""

from __future__ import annotations

import logging

from flask import (
    render_template,
    request,
    url_for,
)

logger = logging.getLogger(__name__)

def email_msg_dashboard() -> str:
    return render_template(
        "admins/email_msg.html",
    )

__all__ = [
    "email_msg_dashboard",
]
