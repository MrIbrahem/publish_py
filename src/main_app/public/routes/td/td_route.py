"""
Translation Dashboard routes (MethodView-based).

Provides the dashboard landing page, the results table view, the
"missing articles" overview, and the JSON results API. Shared request
parsing and database services live on ``BaseTDView``; each page is a
dedicated ``MethodView`` registered through the ``TDRoutes`` registrar.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from flask import (
    Blueprint,
    flash,
    jsonify,
    render_template,
    request,
)
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from ....database.services import (
    CategoryService,
    FullTranslatorService,
    LangService,
    MissingStatsService,
    SettingsService,
)
from ....services.auth.utils import get_current_user
from .results_2026 import ResultsBundle, ResultsLoader
from .results_api import results_api_result

logger = logging.getLogger(__name__)


def _normalize_arg(name: str) -> str:
    """Read a GET param, strip whitespace, treat 'undefined' as empty.

    Mirrors the PHP load_request normalization (htmlspecialchars + the
    explicit `if ($code == "undefined") $code = "";`).
    """
    raw = (request.args.get(name) or "").strip()
    if raw == "undefined":
        return ""
    return raw


def _as_bool(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class BaseTDView(MethodView):
    """Base view for the translation dashboard.

    Holds the services shared by every dashboard page and exposes the
    request-parsing helper that mirrors ``load_request.php``.
    """

    def __init__(self) -> None:
        self.full_service = FullTranslatorService()
        self.missing_service = MissingStatsService()
        self.settings_service = SettingsService()
        self.lang_service = LangService()
        self.category_service = CategoryService()

    def _load_langs_and_campaigns(self) -> tuple[list[dict], list[dict]]:
        """Load the language and campaign lists used by the filter form.

        Returns empty lists and flashes a warning when the lookup fails so a
        database hiccup never breaks the whole page.
        """
        try:
            langs = [x.to_json() for x in self.lang_service.list_langs()]
            campaigns_records = self.category_service.list_categories()
            campaigns = [x.to_json() for x in campaigns_records]
        except Exception:
            logger.exception("Failed to load languages/campaigns for index page")
            flash("Failed to load page data — please try again.", "danger")
            langs = []
            campaigns = []
        return langs, campaigns

    def _build_form_data(
        self,
        langs: list[dict],
        campaigns: list[dict],
        parsed: dict[str, Any],
        full_tr_user: bool,
    ) -> dict[str, Any]:
        """Assemble the template context consumed by the filter form."""
        return {
            "langs": langs,
            "campaigns": campaigns,
            "full_tr_user": full_tr_user,
            "args": {
                "code": parsed["code"],
                "camp": parsed["camp"],
                "cat": parsed["cat"],
                "tra_type": parsed["tra_type"],
            },
        }

    def _parse_request_args(self, campaigns: list[dict]) -> dict[str, Any]:
        """Mirror of src/backend/loaders/load_request.php — load_request().

        Returns a dict with the resolved request parameters. ``code_lang_name``
        is empty when the code is unknown; the route uses this to decide
        whether to render the results card.
        """

        # Lookup tables used by request parsing (PHP $camps_data and $cats_data).
        camps_data: dict[str, dict] = {c["campaign"]: c for c in campaigns if c.get("campaign")}
        cats_data: dict[str, str] = {c["category"]: c.get("campaign", "") for c in campaigns if c.get("category")}

        code = _normalize_arg("code")
        camp = _normalize_arg("camp")
        cat = _normalize_arg("cat")
        tra_type = _normalize_arg("tra_type")

        filter_sparql = _as_bool(_normalize_arg("filter_sparql"))

        code_lang_name = ""

        if code:
            lang_record = self.lang_service.get_lang_by_code(code)
            if lang_record is None:
                flash(f"code ({code}) not valid wiki.", "danger")
                code = ""
            else:
                code_lang_name = lang_record.name or lang_record.autonym or ""

        # logic from load_request.php — cross-resolve cat <-> camp.
        if not cat and camp:
            cat = camps_data.get(camp, {}).get("category", "") or cat
        if cat and not camp:
            camp = cats_data.get(cat, "") or camp

        # logic from load_request.php — validate camp against the input list.
        if camp and camp not in camps_data:
            flash(f"camp ({camp}) not valid.", "danger")
            camp = ""

        # logic from load_request.php — force "lead" when whole-article translate is disabled.

        def to_bool(val: Any) -> bool:
            if isinstance(val, str):
                return val.lower() in ("1", "true", "yes", "on")
            return bool(val)

        all_settings = self.settings_service.get_all_settings_ready()

        show_translation_button = to_bool(all_settings.get("translation_button_in_progress_table", False))
        allow_type_of_translate = to_bool(all_settings.get("allow_type_of_translate", False))
        show_exists_table = to_bool(all_settings.get("show_exists_table", False))

        if not allow_type_of_translate:
            tra_type = "lead"

        return {
            "code": code,
            "code_lang_name": code_lang_name,
            "camp": camp,
            "cat": cat,
            "tra_type": tra_type,
            "settings": {
                "filter_sparql": filter_sparql,
                "show_exists_table": show_exists_table,
                "allow_type_of_translate": allow_type_of_translate,
                "show_translation_button": show_translation_button,
            },
        }


class TDIndexView(BaseTDView):
    """Render the translation dashboard landing page."""

    def get(self) -> str:
        """Render the dashboard with the filter form and no results card."""
        langs, campaigns = self._load_langs_and_campaigns()
        parsed = self._parse_request_args(campaigns)

        # Identity / coordinator / full-translator flags — mirrors src/index.php.
        user = get_current_user()
        full_tr_user = bool(user and self.full_service.is_full_translator(user.username))

        form_data = self._build_form_data(langs, campaigns, parsed, full_tr_user)
        return render_template(
            "td/index.html",
            settings=parsed["settings"],
            form_data=form_data,
        )


class TDTableView(BaseTDView):
    """Render the dashboard with the results table for a code/campaign pair."""

    def get(self) -> str:
        """Render the dashboard and load the results bundle when valid."""
        langs, campaigns = self._load_langs_and_campaigns()

        parsed = self._parse_request_args(campaigns)

        # Identity / coordinator / full-translator flags — mirrors src/index.php.
        user = get_current_user()
        full_tr_user = bool(user and self.full_service.is_full_translator(user.username))

        # PHP: only invoke results_loader_27 when both code and camp are valid.
        results_bundle: ResultsBundle | None = None
        if parsed["code"] and parsed["camp"] and parsed["code_lang_name"]:
            results_bundle = self._load_results(parsed, full_tr_user)

        if results_bundle and results_bundle.summary_data:
            results_bundle.summary_data["code_lang_name"] = parsed["code_lang_name"]

        form_data = self._build_form_data(langs, campaigns, parsed, full_tr_user)
        return render_template(
            "td/index.html",
            settings=parsed["settings"],
            form_data=form_data,
            results=results_bundle,
        )

    def _load_results(self, parsed: dict[str, Any], full_tr_user: bool) -> ResultsBundle | None:
        """Load the results bundle, flashing a warning on failure."""
        try:
            return ResultsLoader().load(
                code=parsed["code"],
                cat=parsed["cat"],
                tra_type=parsed["tra_type"],
                code_lang_name=parsed["code_lang_name"],
                settings=parsed["settings"],
                full_tr_user=full_tr_user,
            )
        except Exception:
            logger.exception(
                "results_loader_27 failed for code=%r camp=%r cat=%r",
                parsed["code"],
                parsed["camp"],
                parsed["cat"],
            )
            flash("Failed to load results — please try again.", "danger")
            return None


class TDMissingView(BaseTDView):
    """Render the "top languages by missing articles" overview."""

    def get(self) -> str:
        """Render the missing-statistics page for a category."""
        # logic from src/missing.php — Top languages by missing articles in Category:RTT.
        category = request.args.get("cat") or "RTT"

        try:
            stats = self.missing_service.statics_by_category(category)
        except Exception:
            logger.exception("statics_by_category failed for cat=%r", category)
            flash("Failed to load missing statistics — please try again.", "danger")
            stats = []

        try:
            total = self.missing_service.count_category_members(category)
        except Exception:
            logger.exception("count_category_members failed for cat=%r", category)
            total = 0

        # PHP merges per-language stats with the langs lookup (autonym + name).
        langs_lookup: dict[str, dict] = {}
        try:
            for lang in self.lang_service.list_langs():
                data = lang.to_json()
                code = data.get("code")
                if code:
                    langs_lookup[code] = data
        except Exception:
            logger.exception("list_langs failed while building missing-stats page")

        rows: list[dict] = []
        for stat in stats:
            langcode = stat.get("language_code") or ""
            if not langcode:
                continue
            lang_data = langs_lookup.get(langcode, {})
            autonym = lang_data.get("autonym") or "! autonym"
            langname = lang_data.get("name") or "! langname"
            exists = int(stat.get("available_title_count") or 0)
            # PHP: $missing = (int)$length - (int)$exists;
            missing_count = max(total - exists, 0)
            rows.append(
                {
                    "langcode": langcode,
                    "langname": langname,
                    "autonym": autonym,
                    "exists": exists,
                    "missing": missing_count,
                }
            )

        return render_template(
            "td/missing.html",
            category=category,
            total=total,
            rows=rows,
        )


class TDResultsApiView(BaseTDView):
    """Expose the results bundle as JSON for AJAX clients."""

    def get(self) -> ResponseReturnValue:
        """Return the results for a code/campaign/depth triple as JSON."""
        code = request.args.get("code")
        camp = request.args.get("camp")
        depth = request.args.get("depth")

        start = time.time()

        try:
            result_dict = results_api_result(code, camp, depth)
        except Exception:
            logger.exception(
                "results_api_result failed for code=%r camp=%r depth=%r",
                code,
                camp,
                depth,
            )
            return jsonify({"error": "Failed to load results"}), 500

        elapsed = time.time() - start

        return jsonify(
            {
                "execution_time": round(elapsed, 6),
                "results": result_dict,
            }
        )


class TDRoutes:
    """Registrar wiring the dashboard MethodViews onto a blueprint.

    Endpoint names (``index``, ``table``, ``missing``, ``results_api``) are
    preserved from the legacy function-based routes so existing
    ``url_for('td.index')`` / ``url_for('td.table')`` calls keep working.
    """

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register all translation dashboard views on the blueprint."""
        bp.add_url_rule("/", view_func=TDIndexView.as_view("index"))
        bp.add_url_rule("/table", view_func=TDTableView.as_view("table"))
        bp.add_url_rule("/missing", view_func=TDMissingView.as_view("missing"))
        bp.add_url_rule("/results_api", view_func=TDResultsApiView.as_view("results_api"))


__all__ = [
    "TDRoutes",
    "TDIndexView",
    "TDTableView",
    "TDMissingView",
    "TDResultsApiView",
]
