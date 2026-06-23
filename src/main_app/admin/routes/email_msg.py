"""
"""

from __future__ import annotations

import logging
from typing import Any

from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
)

from ..decorators import admin_required

from ...shared.auth.identity import current_user

from ...db.services.users import get_user_by_username

from ...db.services.pages import get_page_by_id, get_user_page_by_id

logger = logging.getLogger(__name__)

bp_msg = Blueprint("email_msg", __name__, url_prefix="/email_msg")


def  create_email_msg(user: str, page_data: dict[str, Any]) -> str:
    return ""

def msg_dashboard(user: str, last_table: str, id: int) -> str:
    # http://127.0.0.1:5000/admin/email_msg?user=Mr.+Ibrahem&id=10653&last_table=pages

    logger.info(f"user={user}, id={id}, last_table={last_table}")
    # Fetch data based on table type

    if last_table == "pages":
        page_record = get_page_by_id(id)
    else:
        page_record = get_user_page_by_id(id)
    # user=row.user, lang=row.lang, target=row.target, date=row.pupdate, title=row.title

    user_record = get_user_by_username(user)
    user_email = user_record.email if user_record else None

    currect_user_email = None
    currect_user = current_user()
    if currect_user:
        _user = get_user_by_username(currect_user.username)
        currect_user_email = _user.email if _user else None

    # Create email message
    page_data = page_record.to_dict() if page_record else {}
    msg = create_email_msg(user, page_data)

    return render_template(
        "admins/email_msg.html",
        user_email=user_email,
        cc_me_email=currect_user_email,
        msg=msg,
    )


@bp_msg.route("/", methods=["GET"])
@admin_required
def index() -> str:
    user = request.args.get("user")
    last_table = request.args.get("last_table")
    id = request.args.get("id")

    return msg_dashboard(user, last_table, id)


@bp_msg.route("/dashboard/<string:user>/<string:last_table>/<int:id>", methods=["GET"])
@admin_required
def dashboard(user: str, last_table: str, id: int) -> str:
    return msg_dashboard(user, last_table, id)


@bp_msg.route("/send", methods=["POST"])
@admin_required
def msg_post() -> str:
    return render_template(
        "admins/email_msg.html",
        user_email=None,
        cc_me_email=None,
        msg=None,
    )


__all__ = [
    "bp_msg",
]
