"""Admin routes for email message operations using Flask MethodViews."""

from __future__ import annotations

import logging
from typing import Any


from ....database.services import PagesService, UserPagesService, UsersService, ViewsNewService
from ....public.routes.td.results_api import results_api_result
from ....services.auth.utils import get_current_user
from ....services.utils.wiki_links import tr_link_medwiki

logger = logging.getLogger(__name__)


def send_msg(
    msg: str,
    email_to: str,
    email_from: str,
    msg_title: str,
    cc_to: str | None,
): ...


def make_sugustion(langcode: str | None, title: str | None) -> str | None:

    if not langcode or not title:
        return None

    data = results_api_result(langcode, "Main", 0)

    missing = [x for x in data.get("missing", []) if x != title]
    return missing[0] if missing else None


def get_user_email(username: str) -> str | None:
    users_service = UsersService()
    user_record = users_service.get_user_by_username(username)
    user_email = user_record.email if user_record else None
    return user_email


def get_current_user_email() -> str | None:
    current_user = get_current_user()

    if current_user:
        return get_user_email(current_user.username)

    return None


def get_page_data(last_table: str, id: int) -> dict[str, str | Any]:
    if last_table == "pages":
        pages_service = PagesService()
        page_record = pages_service.get_page_by_id(id)
    else:
        user_pages_service = UserPagesService()
        page_record = user_pages_service.get_page_by_id(id)
    # user=row.user, lang=row.lang, target=row.target, date=row.pupdate, title=row.title
    page_data = page_record.to_json() if page_record else {}
    target = page_data.get("target")
    lang = page_data.get("lang")

    if page_data and target and not page_data.get("views"):
        page_data["views"] = ViewsNewService().get_total_views_for_target(target, lang)

    return page_data


def create_blank_link(url: str, title: str) -> str:
    return f"<a target='_blank' href='{url}'>{title}</a>"


def create_email_msg(page_data: dict[str, Any], sugust: str | None) -> str:
    if not sugust:
        return ""
    title = page_data.get("title", "")
    langcode = page_data.get("lang", "")
    langname = page_data.get("langname", "") or langcode
    target = page_data.get("target", "")
    date = page_data.get("date", "")
    views = page_data.get("views", "many")

    title_link = create_blank_link(f"https://mdwiki.org/wiki/{title}", title)
    sugust_link = create_blank_link(f"https://mdwiki.org/wiki/{sugust}", sugust)
    target_link = create_blank_link(f"https://{langcode}.wikipedia.org/wiki/{target}", langname)
    translate_link = create_blank_link(
        tr_link_medwiki(
            title=sugust,
            langcode=langcode,
            cat="RTT",
            camp="Main",
            tra_type="lead",
            word=0,
        ),
        "HERE",
    )

    msg = (
        "<font color='#0000ff'>Thank you</font>"
        f" for your prior translation of {title_link} into {target_link}.<br>"
        " Since this translation has gone live on"
        f" <font color='#311873'>{date}</font>"
        f" it has been read by <font color='#0000ff'>{views} people</font>.<br>"
        f' Would you be interested in translating "{sugust_link}"?'
        f" If so, simply click {translate_link}.<br>"
        " Once again thank you for improving access to knowledge.<br>"
    )
    return msg


__all__ = [
    "send_msg",
    "make_sugustion",
    "get_user_email",
    "get_current_user_email",
    "get_page_data",
    "create_blank_link",
    "create_email_msg",
]
