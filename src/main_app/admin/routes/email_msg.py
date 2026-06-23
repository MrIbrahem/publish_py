""" """

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlencode

from flask import (
    Blueprint,
    render_template,
    request,
)

from ...db.services.pages import get_page_by_id, get_user_page_by_id
from ...db.services.users import get_user_by_username
from ...shared.auth.identity import current_user
from ..decorators import admin_required

logger = logging.getLogger(__name__)

bp_msg = Blueprint("email_msg", __name__, url_prefix="/email_msg")


def make_translate_link(sugust: str, langcode: str) -> str:
    params = {
        "code": langcode,
        "cat": "RTT",
        "type": "lead",
        "title": sugust,
    }
    here_url = "https://mdwiki.toolforge.org/Translation_Dashboard/translate_med/index.php?" + urlencode(params)
    return here_url

def make_sugustion(langcode: str) -> str | None:
    return "test"

def get_user_email(username: str) -> str | None:
    user_record = get_user_by_username(username)
    user_email = user_record.email if user_record else None
    return user_email


def get_currect_user_email() -> str | None:
    currect_user = current_user()

    if currect_user:
        return get_user_email(currect_user.username)

    return None


def get_page_data(last_table: str, id: int) -> dict[str, Any]:
    if last_table == "pages":
        page_record = get_page_by_id(id)
    else:
        page_record = get_user_page_by_id(id)
    # user=row.user, lang=row.lang, target=row.target, date=row.pupdate, title=row.title
    page_data = page_record.to_dict() if page_record else {}
    return page_data


def create_blank_link(url: str, title: str) -> str:
    return f"<a target='_blank' href='{url}'>{title}</a>"

def create_email_msg(page_data: dict[str, Any], sugust: str) -> str:
    title = page_data.get("title", "")
    langcode = page_data.get("lang", "")
    langname = page_data.get("langname", "") or langcode
    target = page_data.get("target", "")
    date = page_data.get("date", "")
    views = page_data.get("views", "many")

    title_link = create_blank_link(f"https://mdwiki.org/wiki/{title}", title)
    sugust_link = create_blank_link(f"https://mdwiki.org/wiki/{sugust}", sugust)
    target_link = create_blank_link(f"https://{langcode}.wikipedia.org/wiki/{target}", langname)
    translate_link = create_blank_link(make_translate_link(sugust, langcode), "HERE")

    msg = (
        "<font color='#0000ff'>Thank you</font>"
        f" for your prior translation of {title_link} into {target_link}.<br>"
        " Since this translation has gone live on"
        f" <font color='#311873'>{date}</font>"
        f" it has been read by <font color='#0000ff'>{views} people</font>.<br>"
        f" Would you be interested in translating '{sugust_link}'?"
        f" If so, simply click {translate_link}.<br>"
        " Once again thank you for improving access to knowledge.<br>"
    )
    return msg


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

    sugust = make_sugustion(page_data.get("lang"))

    # Create email message
    msg = create_email_msg(page_data, sugust)

    return render_template(
        "admins/email_msg/index.html",
        username=username,
        user_email=user_email,
        cc_me_email=currect_user_email,
        html_mag=msg,
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
    data = request.form
    msg = data.get("msg", "")
    email_to = data.get("email_to", "")
    email_from = data.get("email_from", "mdwiki.org@gmail.com")
    msg_title = data.get("msg_title", "Wiki Project Med Translation Dashboard")
    ccme = data.get("ccme", "0")
    cc_to = data.get("cc_to", "") if str(ccme) == "1" else None

    return render_template(
        "admins/email_msg/index.html",
        user_email=None,
        cc_me_email=None,
        msg=None,
    )


__all__ = [
    "bp_msg",
]
