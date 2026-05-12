"""
Results API — mirrors PHP Results\GetResults\get_results_new.
"""

from __future__ import annotations

import logging
from typing import Any

from ....shared.clients import get_mdwiki_cat_members
from ....shared.services import get_camp_to_cats, list_in_process_by_lang, list_pages_by_lang_cat, list_targets_by_lang

logger = logging.getLogger(__name__)


def results_api_result(
    code: str | None,
    camp: str | None,
    depth: str | None,
    cat2: str | None = None,
) -> dict[str, Any]:
    code = code or "ar"
    camp = camp or "Hearing"
    try:
        depth_int = max(0, int(depth)) if depth else 1
    except (ValueError, TypeError):
        depth_int = 1

    cat = _resolve_campaign_to_category(camp)

    pages = list_pages_by_lang_cat(code, cat)
    pages_by_title = {p.title: p for p in pages}

    items_exists, items_missing = _get_cat_exists_and_missing(pages_by_title, cat, depth_int, code)

    targets = _get_exists_targets_by_lang(code)
    extra_exists = _exists_expends(items_missing, targets)

    if extra_exists:
        items_exists.update(extra_exists)
        items_missing = [t for t in items_missing if t not in extra_exists]

    missing = _unique_ordered(items_missing)

    inprocess = _get_inprocess_for_titles(missing, code)
    in_titles = set(inprocess)
    missing = [t for t in missing if t not in in_titles]

    summary = _make_summary(code, cat, len(inprocess), len(missing), len(items_exists))

    return {
        "inprocess": inprocess,
        "exists": dict(sorted(items_exists.items())),
        "missing": missing,
        "ix": summary,
    }


def _resolve_campaign_to_category(camp: str) -> str:
    cats = get_camp_to_cats()
    return cats.get(camp, camp)


def _get_cat_exists_and_missing(
    pages_by_title: dict[str, Any],
    cat: str,
    depth: int,
    code: str,
) -> tuple[dict, list]:
    if not pages_by_title:
        pages_by_title = {p.title: p for p in list_pages_by_lang_cat(code, cat)}

    members = get_mdwiki_cat_members(cat, depth, use_cache=True)
    member_set = set(members)

    exists = {}
    for title, page in pages_by_title.items():
        if title in member_set:
            exists[title] = {
                "qid": getattr(page, "qid", "") or "",
                "title": page.title or "",
                "target": page.target or "",
                "via": "td",
                "pupdate": page.pupdate or "",
                "user": page.user or "",
            }

    missing = list(member_set - set(exists.keys()))

    return exists, missing


def _get_exists_targets_by_lang(lang: str) -> dict[str, dict]:
    rows = list_targets_by_lang(lang)
    result = {row["title"]: row for row in rows}
    return result


def _exists_expends(
    missing: list[str],
    targets: dict[str, dict],
) -> dict[str, dict]:
    result = {}
    for title in missing:
        entry = targets.get(title)
        if entry and entry.get("target"):
            result[title] = {
                "qid": entry.get("qid", ""),
                "title": entry.get("title", ""),
                "target": entry["target"],
                "via": "before",
            }
    return result


def _get_inprocess_for_titles(missing: list[str], code: str) -> dict[str, dict]:
    records = list_in_process_by_lang(code)

    missing_set = set(missing)
    return {
        r.title: {
            "id": r.id,
            "title": r.title,
            "user": r.user,
            "lang": r.lang,
            "cat": r.cat,
            "translate_type": r.translate_type,
            "word": r.word,
            "add_date": r.add_date.isoformat() if r.add_date else None,
        }
        for r in records
        if r.title in missing_set
    }


def _unique_ordered(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _make_mdwiki_cat_url(category: str, name: str | None = None) -> str:
    if not category:
        return ""
    clean = category.replace("Category:", "")
    display = name or clean
    from urllib.parse import quote

    encoded = quote(clean.replace(" ", "_"), safe="")
    return f"<a target='_blank' " f"href='https://mdwiki.org/wiki/Category:{encoded}'>{display}</a>"


def _make_summary(code: str, cat: str, inprocess_count: int, missing_count: int, exists_count: int) -> str:
    total = exists_count + missing_count + inprocess_count
    cat_url = _make_mdwiki_cat_url(cat, "Category")
    return (
        f"Found {total} pages in {cat_url}, "
        f"{exists_count} exists, and {missing_count} missing in "
        f"(<a href='https://{code}.wikipedia.org' "
        f"target='_blank'>{code}</a>), "
        f"{inprocess_count} In process."
    )


__all__ = [
    "results_api_result",
]
