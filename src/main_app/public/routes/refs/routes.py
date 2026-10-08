"""
Routes for the 'Fix References' feature.
This blueprint provides a user interface for processing text to fix references
using the `do_changes_to_text_with_settings` service.
"""

from __future__ import annotations

import logging
import random

from flask import (
    Blueprint,
    flash,
    render_template,
    request,
)
from flask.views import MethodView

from ....public.auth import oauth_required
from ....services.clients.text_api import get_wikitext
from ....services.utils.helpers.text_processor import (
    do_changes_to_text_with_settings,
)

logger = logging.getLogger(__name__)


def _process(data) -> str:
    source_title = data.get("source_title", "")
    title = data.get("title", "")
    text = data.get("text", "")
    lang = data.get("lang", "")
    mdwiki_revid_raw = data.get("mdwiki_revid", "").strip()

    try:
        mdwiki_revid = int(mdwiki_revid_raw or 0)
    except ValueError:
        flash("Invalid MDWiki revision ID.", "warning")
        mdwiki_revid = 0

    save = data.get("save", "").lower() in {"1", "true", "on", "yes"}
    infobox = data.get("infobox", "").lower() in {"1", "true", "on", "yes"}
    movedots = data.get("movedots", "").lower() in {"1", "true", "on", "yes"}
    # add_en_lang = data.get("add_en_lang", "").lower() in {"1", "true", "on", "yes"}
    # add_category = data.get("add_category", "").lower() in {"1", "true", "on", "yes"}

    if not text and lang and title:
        text = get_wikitext(title, project=f"{lang}.wikipedia.org") or ""

    try:
        result = do_changes_to_text_with_settings(
            text=text,
            title=title,
            lang=lang,
            source_title=source_title,
            mdwiki_revid=mdwiki_revid,
            move_dots=movedots,
            expend_infobox=infobox,
            # add_en_lang=add_en_lang,
            # add_category=add_category,
        )
    except Exception:
        logger.exception("Error processing text")
        result = "An error occurred while processing the text. Please check the logs for details."

    result = result or ""
    no_changes = result.strip() == text.strip()

    if no_changes:
        flash("No changes were made to the text.", "warning")

    return render_template(
        "fixrefs/index.html",
        no_changes=no_changes,
        source_title=source_title,
        title=title,
        lang=lang,
        mdwiki_revid=mdwiki_revid,
        text=text,
        result=result,
        form={
            "save": save,
            "infobox": infobox,
            "movedots": movedots,
        },
    )


class FixRefsIndexView(MethodView):
    """Render the Fix References landing page."""

    def get(self) -> str:
        """Render the empty fix-refs form."""
        return render_template(
            "fixrefs/index.html",
            result=None,
            form={},
        )


class FixRefsTestView(MethodView):
    """Render the form prefilled with a random test case."""

    def get(self) -> str:
        """Pick one of the bundled test fixtures and render the form."""
        tests_data = [
            {
                "source_title": "Decitabine/cedazuridine",
                "title": "Decitabina/cedazuridina",
                "lang": "es",
                "mdwiki_revid": 1478161,
                "text": "",
            },
            {
                "source_title": "Tropicamide",
                "title": "Usuario:Mr. Ibrahem/Tropicamida",
                "lang": "es",
                "mdwiki_revid": 1408734,
                "text": "",
            },
            {
                "source_title": "Fatty liver disease",
                "title": "Մասնակից:Mr. Ibrahem/Լյարդի ճարպային հիվանդություն",
                "lang": "hy",
                "mdwiki_revid": 1458412,
                "text": "",
            },
            {
                "source_title": "Malnutrition",
                "title": "مستخدم:Mr. Ibrahem/سوء التغذية",
                "lang": "ar",
                "mdwiki_revid": 1503213,
                "text": "zz.<ref name=Bh2013/>",
            },
        ]
        item = random.choice(tests_data)

        return render_template(
            "fixrefs/index.html",
            **item,
            form={
                "infobox": 1,
            },
        )


class FixRefsProcessNewView(MethodView):
    """Process text submitted through the form (POST body)."""

    decorators = [oauth_required]

    def post(self) -> str:
        """Run the fix pipeline on the submitted form data."""
        data = request.form.to_dict()
        logger.info("Processing text with settings: %s", data)
        return _process(data)


class FixRefsProcessView(MethodView):
    """Process text supplied through query parameters."""

    decorators = [oauth_required]

    def get(self) -> str:
        """Run the fix pipeline on the query-string data."""
        data = request.args
        logger.info("Processing text with settings: %s", data)
        return _process(data)


class FixRefsRoutes:
    """Registrar for the Fix References views."""

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register the fix-refs endpoints on the blueprint.

        Endpoint names mirror the legacy function names so existing
        ``url_for('fixrefs.index')`` / ``url_for('fixrefs.process_new')``
        calls keep resolving.
        """
        bp.add_url_rule("/", view_func=FixRefsIndexView.as_view("index"))
        bp.add_url_rule("/test", view_func=FixRefsTestView.as_view("test"))
        bp.add_url_rule("/", view_func=FixRefsProcessNewView.as_view("process_new"), methods=["POST"])
        bp.add_url_rule("/process", view_func=FixRefsProcessView.as_view("process"))


__all__ = [
    "FixRefsRoutes",
]
