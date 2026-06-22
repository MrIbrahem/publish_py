"""
Defines the main routes for the application, such as the homepage.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

from flask import (
    Blueprint,
    flash,
    jsonify,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from ....db.services.config import get_setting_by_key
from ....db.services.content import get_lang_by_code, list_categories, list_langs
from ....db.services.pages import (
    count_category_members,
    statics_by_category,
)
from ....db.services.users import active_coordinators, is_full_translator
from ....app_routes.auth.identity import current_user
from .results_2026 import results_loader_2026
from .results_api import results_api_result

bp_main = Blueprint("main", __name__, url_prefix="")
logger = logging.getLogger(__name__)


@bp_main.get("/results_api")
def results_api():
    code = request.args.get("code")
    camp = request.args.get("camp")
    depth = request.args.get("depth")

    start = time.time()
    result_dict = results_api_result(code, camp, depth)
    elapsed = time.time() - start

    return jsonify(
        {
            "execution_time": round(elapsed, 6),
            "results": result_dict,
        }
    )


def _setting_value(key: str, default: str = "") -> str:
    """Fetch a settings row by key, returning the stringified value."""
    try:
        record = get_setting_by_key(key)
    except Exception:
        logger.exception("Setting lookup failed for key=%r", key)
        return default
    if record is None or record.value is None:
        return default
    return record.value


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


def _parse_request_args(camps_data: dict[str, dict], cats_data: dict[str, str]) -> dict[str, Any]:
    """Mirror of src/backend/loaders/load_request.php — load_request().

    Returns a dict with the resolved request parameters. ``code_lang_name``
    is empty when the code is unknown; the route uses this to decide
    whether to render the results card.
    """
    code = _normalize_arg("code")
    camp = _normalize_arg("camp")
    cat = _normalize_arg("cat")
    tra_type = _normalize_arg("type")

    filter_sparql = _as_bool(_normalize_arg("filter_sparql"))

    show_exists_param = "exists" in request.args

    code_lang_name = ""

    if code:
        lang_record = get_lang_by_code(code)
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
    allow_whole_translate = _setting_value("allow_type_of_translate", "1")
    if allow_whole_translate == "0":
        tra_type = "lead"

    return {
        "code": code,
        "code_lang_name": code_lang_name,
        "camp": camp,
        "cat": cat,
        "tra_type": tra_type,
        "filter_sparql": filter_sparql,
        "show_exists_param": show_exists_param,
        "allow_whole_translate": allow_whole_translate,
    }


def _resolve_translation_button(user_coord: bool) -> str:
    """Mirror of src/index.php translation_button gate."""
    raw = _setting_value("translation_button_in_progress_table", "0")
    if raw == "0":
        return "0"
    return "1" if user_coord else "0"


@bp_main.get("/table")
def table():
    # Form data — unchanged from the previous index() implementation.
    try:
        langs = [x.to_dict() for x in list_langs()]
        campaigns_records = list_categories()
        campaigns = [x.to_dict() for x in campaigns_records]
    except Exception:
        logger.exception("Failed to load languages/campaigns for index page")
        flash("Failed to load page data — please try again.", "danger")
        langs = []
        campaigns = []

    # Lookup tables used by request parsing (PHP $camps_data and $cats_data).
    camps_data: dict[str, dict] = {c["campaign"]: c for c in campaigns if c.get("campaign")}
    cats_data: dict[str, str] = {c["category"]: c.get("campaign", "") for c in campaigns if c.get("category")}

    parsed = _parse_request_args(camps_data, cats_data)

    # Identity / coordinator / full-translator flags — mirrors src/index.php.
    user = current_user()
    user_coord = bool(user and user.username in active_coordinators())
    show_exists = user_coord or parsed["show_exists_param"]
    translation_button = _resolve_translation_button(user_coord)
    full_tr_user = bool(user and is_full_translator(user.username))

    # PHP: only invoke results_loader_2026 when both code and camp are valid.
    results_bundle = None
    if parsed["code"] and parsed["camp"] and parsed["code_lang_name"]:
        try:
            results_bundle = results_loader_2026(
                code=parsed["code"],
                camp=parsed["camp"],
                cat=parsed["cat"],
                tra_type=parsed["tra_type"],
                code_lang_name=parsed["code_lang_name"],
                user_coord=user_coord,
                show_exists=show_exists,
                translation_button=translation_button,
                full_tr_user=full_tr_user,
            )
        except Exception:
            logger.exception(
                "results_loader_2026 failed for code=%r camp=%r cat=%r",
                parsed["code"],
                parsed["camp"],
                parsed["cat"],
            )
            flash("Failed to load results — please try again.", "danger")

    return render_template(
        "index.html",
        settings={
            "allow_whole_translate": parsed["allow_whole_translate"] != "0",
        },
        langs=langs,
        campaigns=campaigns,
        args={
            "code": parsed["code"],
            "camp": parsed["camp"],
            "type": parsed["tra_type"],
        },
        results=results_bundle,
    )


@bp_main.get("/")
def index():
    # Form data — unchanged from the previous index() implementation.
    try:
        langs = [x.to_dict() for x in list_langs()]
        campaigns_records = list_categories()
        campaigns = [x.to_dict() for x in campaigns_records]
    except Exception:
        logger.exception("Failed to load languages/campaigns for index page")
        flash("Failed to load page data — please try again.", "danger")
        langs = []
        campaigns = []

    # Lookup tables used by request parsing (PHP $camps_data and $cats_data).
    camps_data: dict[str, dict] = {c["campaign"]: c for c in campaigns if c.get("campaign")}
    cats_data: dict[str, str] = {c["category"]: c.get("campaign", "") for c in campaigns if c.get("category")}

    parsed = _parse_request_args(camps_data, cats_data)

    return render_template(
        "index.html",
        settings={
            "allow_whole_translate": parsed["allow_whole_translate"] != "0",
        },
        langs=langs,
        campaigns=campaigns,
        args={
            "code": parsed["code"],
            "camp": parsed["camp"],
            "type": parsed["tra_type"],
        },
    )


@bp_main.get("/reports")
def reports():
    return render_template(
        "reports.html",
    )


@bp_main.get("/missing")
def missing():
    # logic from src/missing.php — Top languages by missing articles in Category:RTT.
    category = request.args.get("cat") or "RTT"

    try:
        stats = statics_by_category(category)
    except Exception:
        logger.exception("statics_by_category failed for cat=%r", category)
        flash("Failed to load missing statistics — please try again.", "danger")
        stats = []

    try:
        total = count_category_members(category)
    except Exception:
        logger.exception("count_category_members failed for cat=%r", category)
        total = 0

    # PHP merges per-language stats with the langs lookup (autonym + name).
    langs_lookup: dict[str, dict] = {}
    try:
        for lang in list_langs():
            data = lang.to_dict() if hasattr(lang, "to_dict") else dict(lang)
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
        "missing.html",
        category=category,
        total=total,
        rows=rows,
    )


@bp_main.get("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/x-icon")


__all__ = ["bp_main"]
