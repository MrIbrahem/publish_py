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

from .....database.services import (
    InProcessService,
)
from .....services.utils.wiki_links import (
    content_translation_url,
    wikidata_link,
    wikipedia_link,
)
from .rows._common import _is_video, _row_metrics

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
    "get_inprocess_for_missing",
]
