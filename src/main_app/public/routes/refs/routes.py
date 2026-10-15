"""
Routes for the 'Fix References' feature.
This blueprint provides a user interface for processing text to fix references
using the `TextProcessor.fix` service.
"""

from __future__ import annotations

import logging
import random
from typing import Any

from flask import (
    Blueprint,
    flash,
    render_template,
    request,
)
from flask.views import MethodView

from ....services.utils.helpers.text_processor import LangSetting

from ....database.models import PageSharedRecord

from ....database.services import LanguageSettingService, PagesService, UserPagesService
from ....public.auth import oauth_required
from ....services.clients.text_api import TextApiClient
from ....services.utils.helpers.text_processor import (
    TextProcessor,
)

logger = logging.getLogger(__name__)


def safe_bool(value) -> bool:
    return str(value).lower() in {"1", "true", "on", "yes"}


class FixRefsBase(MethodView):
    """
    A base class for handling reference fixing operations in a web application.
    Inherits from MethodView to support HTTP methods like GET, POST, etc.
    """

    def load_lang(self, data: dict[str, Any]) -> LangSetting:
        lang = data.get("lang", "")

        # `expend` from `LanguageSettingRecord`
        infobox = safe_bool(data.get("infobox") or data.get("expend", ""))

        # `move_dots` from `LanguageSettingRecord`
        movedots = safe_bool(data.get("movedots") or data.get("move_dots", ""))

        # add_en_lang = safe_bool(data.get("add_en_lang", ""))
        # add_category = safe_bool(data.get("add_category", ""))

        return TextProcessor.load_lang(
            lang=lang,
            move_dots=movedots,
            expend_infobox=infobox,
            # add_en_lang=add_en_lang,
            # add_category=add_category,
        )

    def _process(self, data: dict[str, Any], lang_setting : LangSetting | None = None) -> str:
        source_title = data.get("source_title", "")
        title = data.get("title", "")
        text = data.get("text", "")
        lang = data.get("lang", "")
        mdwiki_revid_raw = str(data.get("mdwiki_revid", "")).strip()
        save = safe_bool(data.get("save", ""))

        try:
            mdwiki_revid = int(mdwiki_revid_raw or 0)
        except ValueError:
            flash("Invalid MDWiki revision ID.", "warning")
            mdwiki_revid = 0

        if not text and lang and title:
            text = TextApiClient().get_wikitext(title, project=f"{lang}.wikipedia.org") or ""

        if not lang_setting:
            lang_setting = self.load_lang(data)

        def result_template(no_changes: bool = False, result: str = "") -> str:
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
                    "infobox": lang_setting.expend_infobox,
                    "movedots": lang_setting.move_dots,
                },
            )

        if not (lang and title) and not text:
            flash("Please enter a (language and title) or text.", "warning")
            return result_template()

        try:
            result = TextProcessor.fix(
                text=text,
                title=title,
                source_title=source_title,
                mdwiki_revid=mdwiki_revid,
                lang_setting=lang_setting,
            )
        except Exception:
            logger.exception("Error processing text")
            result = "An error occurred while processing the text. Please check the logs for details."

        result = result or ""
        no_changes = result.strip() == text.strip()

        if no_changes:
            flash("No changes were made to the text.", "warning")

        return result_template(
            no_changes=no_changes,
            result=result,
        )


class FixRefsIndexView(FixRefsBase):
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


class FixRefsProcessNewView(FixRefsBase):
    """Process text submitted through the form (POST body)."""

    decorators = [oauth_required]

    def post(self) -> str:
        """Run the fix pipeline on the submitted form data."""
        data = request.form.to_dict()
        logger.info("Processing text with settings: %s", data)
        return self._process(data)


class FixRefsProcessView(FixRefsBase):
    """Process text supplied through query parameters."""

    decorators = [oauth_required]

    def get(self) -> str:
        """Run the fix pipeline on the query-string data."""
        data = request.args
        logger.info("Processing text with settings: %s", data)
        return self._process(data)


class FixRefsProcessByIdView(FixRefsBase):
    """Process text supplied through query parameters."""

    decorators = [oauth_required]

    def get(self, table: str, id: str) -> str:
        """Run the fix pipeline on the query-string data."""
        int_id = int(id) if id.isdigit() else None

        if not int_id:
            flash("Invalid page ID", "warning")
            return render_template(
                "fixrefs/index.html",
            )

        service = PagesService() if table == "pages" else UserPagesService()
        record: PageSharedRecord | None = service.get_by_id(int_id)

        if not record:
            flash("Page not found", "warning")
            return render_template(
                "fixrefs/index.html",
            )

        data = record.to_json()

        data["source_title"] = data.pop("title", None)
        data["title"] = data.pop("target", None)

        langs_service = LanguageSettingService()
        lang_data = langs_service.get_language_setting_by_code(data["lang"]) if data.get("lang") else None

        # data = request.args
        logger.info("Processing text with settings: %s", data)
        language_settings = self.load_lang(lang_data.to_json()) if lang_data else None

        return self._process(data, language_settings)


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
        bp.add_url_rule(
            "/process_by_id/<string:table>/<string:id>", view_func=FixRefsProcessByIdView.as_view("process_by_id")
        )


__all__ = [
    "FixRefsRoutes",
]
