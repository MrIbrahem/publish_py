""" """

from __future__ import annotations

import logging
from typing import Any

from flask import (
    Blueprint,
    render_template,
)

from ...db.services.pages import get_page_by_id, get_user_page_by_id
from ...db.services.users import get_user_by_username
from ...shared.auth.identity import current_user
from ..decorators import admin_required

logger = logging.getLogger(__name__)

bp_msg = Blueprint("email_msg", __name__, url_prefix="/email_msg")


def get_user_email(username) -> str | None:
    user_record = get_user_by_username(username)
    user_email = user_record.email if user_record else None
    return user_email


def get_currect_user_email() -> str | None:
    currect_user = current_user()

    if currect_user:
        return get_user_email(currect_user.username)

    return None


def get_page_data(last_table, id) -> dict[str, Any]:
    if last_table == "pages":
        page_record = get_page_by_id(id)
    else:
        page_record = get_user_page_by_id(id)
    # user=row.user, lang=row.lang, target=row.target, date=row.pupdate, title=row.title
    page_data = page_record.to_dict() if page_record else {}
    return page_data


def create_email_msg(user: str, page_data: dict[str, Any]) -> str:
    return ""


def msg_dashboard(
    last_table: str,
    id: int,
    user: str | None = None,
) -> str:
    # http://127.0.0.1:5000/admin/email_msg?user=Mr.+Ibrahem&id=10653&last_table=pages

    logger.info(f"user={user}, id={id}, last_table={last_table}")
    # Fetch data based on table type

    page_data = get_page_data(last_table, id)
    username = page_data.get("user", "") or user

    user_email = get_user_email(username)
    currect_user_email = get_currect_user_email()

    # Create email message
    msg = create_email_msg(username, page_data)

    return render_template(
        "admins/email_msg.html",
        username=username,
        user_email=user_email,
        cc_me_email=currect_user_email,
        msg=msg,
    )


@bp_msg.route("/dashboard/<string:last_table>/<int:id>", methods=["GET"])
@bp_msg.route("/dashboard/<string:last_table>/<int:id>/<string:user>", methods=["GET"])
@admin_required
def dashboard(
    last_table: str,
    id: int,
    user: str | None = None,
) -> str:
    return msg_dashboard(last_table, id, user=user)


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
