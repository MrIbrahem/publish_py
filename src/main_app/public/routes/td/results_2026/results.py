"""
Python port of the PHP ``Results\\GetResults2026`` module.

Reference PHP files:
  - src/backend/results_2026/index.php           (results_loader_2026, Results_tables_2026, load_translate_type)
  - src/backend/results_2026/get_results_2026.php (get_results_2026, getinprocess_n)
  - src/backend/results_2026/results_table.php   (_make_one_row_results, make_results_table_2026)
  - src/backend/results_2026/results_table_exists.php (make_one_row_exists_2026, make_results_table_exists_2026)
  - src/backend/results_2026/results_table_inprocess.php (make_one_row_new_inprocess, make_results_table_inprocess)
  - src/results/helps.php                        (make_translate_urls)

The orchestrator returns a :class:`ResultsBundle` (the "results bundle") that
``templates/index.html`` consumes via three Jinja partials.
"""

from __future__ import annotations

import logging
from typing import Any

from flask import url_for

from .....database.services import (
    InProcessService,
    TranslateTypeService,
)
from .....services.utils.wiki_links import (
    content_translation_url,
    tr_link_medwiki,
    wikidata_link,
    wikipedia_link,
)

logger = logging.getLogger(__name__)


def get_inprocess_for_missing(missing_titles: set[str], code: str) -> dict[str, dict]:
    """Mirror of PHP ``getinprocess_n($missing, $code)``."""
    service = InProcessService()
    records = service.list_in_process_by_lang(code)
    result: dict[str, dict] = {}
    for r in records:
        if r.title not in missing_titles:
            continue
        result[r.title] = {
            "id": r.id,
            "title": r.title,
            "user": r.user or "",
            "lang": r.lang,
            "cat": r.cat or "",
            "translate_type": r.translate_type or "",
            "word": r.word or 0,
            "add_date": r.add_date,  # datetime or None
        }
    return result


# ---------------------------------------------------------------------------
# load_translate_type — partition translate_type rows into the two sets
# ---------------------------------------------------------------------------


def load_translate_type_sets() -> tuple[set[str], set[str]]:
    """Mirror of PHP ``load_translate_type('no')`` + ``load_translate_type('full')``.

    Returns ``(nolead_titles, full_titles)``.
    """
    nolead: set[str] = set()
    full: set[str] = set()
    try:
        service = TranslateTypeService()
        rows = service.list_translate_types()
    except Exception:
        logger.exception("Failed to load translate_type rows")
        return nolead, full
    for row in rows:
        if row.tt_full == 1:
            full.add(row.tt_title)
        if row.tt_lead == 0:
            nolead.add(row.tt_title)
    return nolead, full


# ---------------------------------------------------------------------------
# Row builders
# ---------------------------------------------------------------------------


def _is_video(title: str) -> bool:
    return title.lower().startswith("video:")


def _row_metrics(title_data: dict, tra_type: str) -> tuple[int, int, str, Any, str]:
    """Pick (words, refs, importance, en_views, qid) per PHP _make_one_row_results."""
    if tra_type == "all":
        words = title_data.get("w_all_words") or 0
        refs = title_data.get("w_all_refs") or title_data.get("r_all_refs") or 0
    else:
        words = title_data.get("w_lead_words") or 0
        refs = title_data.get("r_lead_refs") or 0

    importance = title_data.get("importance") or "Unknown"
    en_views = title_data.get("en_views") if title_data.get("en_views") is not None else ""
    qid = title_data.get("qid") or ""
    return int(words or 0), int(refs or 0), importance, en_views, qid


def _missing_translate_html(
    *,
    title: str,
    langcode: str,
    cat: str,
    camp: str,
    tra_type: str,
    words: int,
    full_tr_user: bool,
    is_video_title: bool,
    user_is_logged_in: bool,
) -> str:
    """Mirror PHP ``_make_one_row_results`` — translate column HTML."""
    # logic from results_table.php — anonymous user
    if not user_is_logged_in:
        login_url = url_for("auth.login")
        return f"<a href='{login_url}' class='btn btn-outline-primary btn-sm'>Login</a>"

    full_url = tr_link_medwiki(title, langcode, cat, camp, "all", words)
    lead_url = tr_link_medwiki(title, langcode, cat, camp, tra_type, words)

    if full_tr_user and not is_video_title:
        return (
            "<div class='inline'>"
            f"<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Lead</a>"
            f"<a href='{full_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Full</a>"
            "</div>"
        )

    return f"<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"


def _make_missing_row_dict(
    *,
    title: str,
    title_data: dict,
    count: int,
    is_full_row: bool,
    tra_type: str,
    langcode: str,
    cat: str,
    camp: str,
    full_tr_user: bool,
    user_is_logged_in: bool,
) -> dict[str, Any]:
    """Build one row dict for the Results table (PHP _make_one_row_results)."""
    is_video_title = _is_video(title)
    effective_tra_type = "all" if is_video_title else (tra_type or "lead")
    words, refs, importance, en_views, qid = _row_metrics(title_data, effective_tra_type)

    translate_html = _missing_translate_html(
        title=title,
        langcode=langcode,
        cat=cat,
        camp=camp,
        tra_type=effective_tra_type,
        words=words,
        full_tr_user=full_tr_user,
        is_video_title=is_video_title,
        user_is_logged_in=user_is_logged_in,
    )

    # PHP "$count = $full && (substr != 'video:') ? '$count.Full' : $count"
    display_n: str = f"{count}.Full" if is_full_row and not is_video_title else str(count)

    return {
        "n": display_n,
        "title": title,
        "translate_html": translate_html,
        "en_views": en_views,
        "importance": importance,
        "words": words,
        "refs": refs,
        "qid_html": wikidata_link(qid),
        "is_full_row": is_full_row,
    }


def build_missing_rows(
    *,
    missing: list[dict],
    langcode: str,
    cat: str,
    camp: str,
    tra_type: str,
    full_tr_user: bool,
    nolead_titles: set[str],
    full_titles: set[str],
    user_is_logged_in: bool,
) -> list[dict[str, Any]]:
    """Mirror of PHP ``make_results_table_2026``."""
    do_full = (tra_type or "lead") != "all"

    # PHP usort by en_views desc.
    sorted_items = sorted(missing, key=lambda r: int(r.get("en_views") or 0), reverse=True)

    # PHP array_column($items, null, 'title') — keep last entry per title.
    items_by_title: dict[str, dict] = {}
    for row in sorted_items:
        title = row.get("title")
        if title:
            items_by_title[title] = row

    rows: list[dict[str, Any]] = []
    numb = 1

    for title, title_data in items_by_title.items():
        if not title:
            continue
        # PHP str_replace('_', ' ', $title)
        display_title = title.replace("_", " ")

        primary_row = _make_missing_row_dict(
            title=display_title,
            title_data=title_data,
            count=numb,
            is_full_row=False,
            tra_type=tra_type,
            langcode=langcode,
            cat=cat,
            camp=camp,
            full_tr_user=full_tr_user,
            user_is_logged_in=user_is_logged_in,
        )

        # PHP: "if (!$do_full || $full_tr_user) { emit and continue; }"
        if not do_full or full_tr_user:
            rows.append(primary_row)
            numb += 1
            continue

        no_lead = display_title in nolead_titles
        is_full_eligible = display_title in full_titles

        # PHP: "if ($no_lead && !$full) continue;"
        if no_lead and not is_full_eligible:
            continue

        if not no_lead:
            rows.append(primary_row)

        if is_full_eligible:
            rows.append(
                _make_missing_row_dict(
                    title=display_title,
                    title_data=title_data,
                    count=numb,
                    is_full_row=True,
                    tra_type="all",
                    langcode=langcode,
                    cat=cat,
                    camp=camp,
                    full_tr_user=full_tr_user,
                    user_is_logged_in=user_is_logged_in,
                )
            )

        numb += 1

    return rows


# ---------------------------------------------------------------------------
# In-process rows
# ---------------------------------------------------------------------------


def _inprocess_translate_html(
    *,
    title: str,
    tra_type: str,
    langcode: str,
    cat: str,
    camp: str,
    words: int,
    tra_btn: str,
    full_tr_user: bool,
    is_video_title: bool,
    endpoint: str,
) -> str:
    """Mirror of PHP ``make_translate_urls`` — inprocess branch only.

    Returns the HTML for the Translate column. When the button is disabled
    or no user is logged in, returns an empty string (the column then
    renders blank).
    """
    if tra_btn != "1":
        return ""

    effective_type = "all" if is_video_title else (tra_type or "lead")
    full_url = content_translation_url(title, langcode, camp, "all", endpoint)
    lead_url = content_translation_url(title, langcode, camp, effective_type, endpoint)

    tab = f"<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"
    if full_tr_user and not is_video_title:
        tab = (
            "<div class='inline'>"
            f"<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Lead</a>"
            f"<a href='{full_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Full</a>"
            "</div>"
        )
    return tab


def _format_inprocess_date(value: Any) -> str:
    """Mirror of PHP ``if (strpos($_date_, ':') !== false) explode(' ', $_date_)[0]``."""
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        # datetime → ISO; PHP receives "YYYY-MM-DD HH:MM:SS".
        text = value.isoformat(sep=" ")
    else:
        text = str(value)
    if ":" in text:
        return text.split(" ", 1)[0]
    return text


def build_inprocess_rows(
    *,
    inprocess: dict[str, dict],
    langcode: str,
    cat: str,
    camp: str,
    tra_btn: str,
    full_tr_user: bool,
    titles_infos: dict[str, dict],
    endpoint: str,
    user_is_logged_in: bool,
) -> list[dict[str, Any]]:
    """Mirror of PHP ``make_results_table_inprocess``."""
    rows: list[dict[str, Any]] = []
    numb = 1

    for title, title_tab in inprocess.items():
        if not title:
            continue

        display_title = title.replace("_", " ")
        title_data = titles_infos.get(title) or titles_infos.get(display_title) or {}

        tra_type = title_tab.get("translate_type") or ""
        is_video_title = _is_video(display_title)
        if is_video_title:
            tra_type = "all"

        words, refs, importance, en_views, qid = _row_metrics(title_data, tra_type or "lead")

        user = title_tab.get("user") or ""

        translate_html = _inprocess_translate_html(
            title=display_title,
            tra_type=tra_type,
            langcode=langcode,
            cat=cat,
            camp=camp,
            words=words,
            tra_btn=tra_btn,
            full_tr_user=full_tr_user,
            is_video_title=is_video_title,
            endpoint=endpoint,
        )

        rows.append(
            {
                "n": str(numb),
                "title": display_title,
                "translate_html": translate_html,
                "en_views": en_views,
                "importance": importance,
                "words": words,
                "refs": refs,
                "qid_html": wikidata_link(qid),
                "user": user,
                "date": _format_inprocess_date(title_tab.get("add_date") or title_tab.get("date")),
                "is_full_row": False,
            }
        )

        numb += 1

    return rows


# ---------------------------------------------------------------------------
# Exists rows
# ---------------------------------------------------------------------------


def build_exists_rows(
    *,
    exists: dict[str, dict],
    langcode: str,
    cat: str,
    camp: str,
    user_coord: bool,
    endpoint: str,
    user_is_logged_in: bool,
) -> tuple[list[dict[str, Any]], int, int]:
    """Mirror of PHP ``make_results_table_exists_2026``.

    Returns ``(rows, count_translated, count_translated_before)``.
    """
    rows: list[dict[str, Any]] = []
    numb = 1
    count_translated = 0
    count_translated_before = 0

    for title, target_tab in exists.items():
        if not title:
            continue

        display_title = title.replace("_", " ")
        via = target_tab.get("via", "")
        target = target_tab.get("target") or ""

        if via == "td":
            count_translated += 1
        else:
            count_translated_before += 1

        translated_html = wikipedia_link(target, langcode) if (target and via == "td") else ""
        translated_before_html = wikipedia_link(target, langcode) if (target and via != "td") else ""

        # PHP: $tab is shown only when user_coord
        if user_coord:
            translate_url = content_translation_url(display_title, langcode, camp, "lead", endpoint)
            translate_html = (
                "<div class='inline'>"
                f"<a href='{translate_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"
                "</div>"
            )
        else:
            translate_html = ""

        rows.append(
            {
                "n": str(numb),
                "display_title": display_title,
                "translate_html": translate_html,
                "translated_html": translated_html,
                "translated_before_html": translated_before_html,
                "qid_html": wikidata_link(target_tab.get("qid") or ""),
            }
        )

        numb += 1

    return rows, count_translated, count_translated_before


__all__ = [
    "build_exists_rows",
    "build_inprocess_rows",
    "build_missing_rows",
    "get_inprocess_for_missing",
    "load_translate_type_sets",
]
