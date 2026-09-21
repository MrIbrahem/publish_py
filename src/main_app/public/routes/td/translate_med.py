"""
Mirror of src/main_app/public/routes/td/translate_med.php.

Redirects a logged-in translator to Special:ContentTranslation after
registering the title in the in_process table — unless the user is an active
member of users_no_inprocess, which PHP skips (lines 216-218).
"""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.views import MethodView
from flask.typing import ResponseReturnValue

from ....database.services import (
    CategoryService,
    InProcessService,
    UsersNoInprocessService,
)
from ....services.auth.utils import get_current_user
from ....services.utils.wiki_links import content_translation_url, get_endpoint

logger = logging.getLogger(__name__)

_DEFAULT_TRA_TYPE = "lead"


def _normalize(name: str) -> str:
    """Read a GET param, strip whitespace, treat ``undefined`` as empty.

    Mirrors the ``load_request`` normalization used across the PHP dashboard
    (``htmlspecialchars`` + ``trim``, plus the explicit ``undefined`` → ``''``
    fallback seen in ``load_request.php``).
    """
    raw = (request.args.get(name, type=str) or "").strip()
    if raw.lower() in ("undefined", "all"):
        return ""
    return raw


def _word(raw: str | None) -> int:
    """PHP ``FILTER_VALIDATE_INT`` with ``min_range`` 0 and default 0."""
    try:
        value = int(raw) if raw is not None else 0
    except (TypeError, ValueError):
        return 0
    return max(value, 0)


class TranslateMedView(MethodView):
    """MethodView to process translation redirection and in-process record registration."""

    def __init__(self) -> None:
        self.in_process_service = InProcessService()
        self.category_service = CategoryService()
        self.no_inprocess_service = UsersNoInprocessService()

    def get(self) -> ResponseReturnValue:
        """Handle translation redirection for logged-in users."""
        user = get_current_user()
        if user is None:
            # PHP lines 169-184: render a login card, then exit.
            return render_template(
                "td/translate_med.html",
                login_url=url_for("auth.login"),
            )

        title = _normalize("title")
        langcode = _normalize("langcode").lower()

        # PHP lines 186-190: both title and code are required; anything else
        # renders an empty page rather than an error.
        if not title or not langcode:
            return render_template("td/translate_med.html")

        cat = _normalize("cat")
        camp = _normalize("camp")
        tra_type = _normalize("tra_type") or _DEFAULT_TRA_TYPE
        word = _word(request.args.get("word"))

        # PHP lines 207-209: $camp = $cats_data[$cat] ?? ""
        if not camp and cat:
            camp = self._campaign_of(cat)

        if not self.no_inprocess_service.should_hide_from_inprocess(user.username):
            self._register_in_process(
                title=title,
                user=user.username,
                lang=langcode,
                cat=cat,
                tra_type=tra_type,
                word=word,
            )

        # PHP prints an intermediate page with a "Click here" link plus a
        # JS/meta auto-redirect; this port issues a straight 302 instead.
        return redirect(
            content_translation_url(
                title=title,
                code=langcode,
                campaign=camp,
                tra_type=tra_type,
                endpoint=get_endpoint(),
            )
        )

    def _campaign_of(self, cat: str) -> str:
        """PHP ``array_column($categories_tab, 'campaign', 'category')`` lookup."""
        record = self.category_service.get_by(category=cat)
        return (record.campaign or "") if record else ""

    def _register_in_process(
        self,
        *,
        title: str,
        user: str,
        lang: str,
        cat: str,
        tra_type: str,
        word: int,
    ) -> None:
        """PHP ``insertPage_inprocess()`` — idempotent ``INSERT ... WHERE NOT EXISTS``.

        The dashboard links fire repeatedly, so a duplicate (title, user, lang)
        triple is the normal case, not an error.
        """
        if self.in_process_service.get_in_process_by_title_user_lang(title, user, lang) is not None:
            return

        try:
            self.in_process_service.add_in_process(
                title=title,
                user=user,
                lang=lang,
                cat=cat,
                translate_type=tra_type,
                word=word,
            )
        except ValueError:
            logger.debug("in_process row already exists for %r/%r/%r", title, user, lang)

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register translation routes on the provided blueprint."""
        bp.add_url_rule("/", view_func=cls.as_view("index"))


__all__ = [
    "TranslateMedView",
]
