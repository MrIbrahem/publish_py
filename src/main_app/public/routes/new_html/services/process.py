"""
Main processing pipeline for the new_html endpoint.

Pipeline:
1. Fetch wikitext + revision
2. WikitextFixerService.fix
3. Convert wikitext → HTML (with cache)
4. Convert HTML → segments (with cache)
5. Return JSON envelope or raw content
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from flask import Response, jsonify

from domain.fixes.references.expand_refs import expand_refs

from ..domain.parser.lead_section_parser import get_lead_section

from ..domain.fixes import WikitextFixerService
from .clients import MdwikiApi, TransformApi
from .html_utils import remove_data_parsoid
from .process_seg import get_segments
from .storage import (
    add_title_revision,
    get_title_revision,
    read_file,
    write_file,
)
from .utils import get_file_dir
from .html_utils import del_div_error, fix_link_red

logger = logging.getLogger(__name__)


def get_from_json(title: str, all_flag: str):
    """
    """
    cached_rev = get_title_revision(title, all_flag)

    if not cached_rev or not cached_rev.isdigit():
        return "", ""

    file_dir = get_file_dir(cached_rev, all_flag)
    if not file_dir.is_dir():
        return "", ""

    cached_text = read_file(file_dir / "wikitext.txt")

    if not cached_text:
        return "", ""

    return cached_text, cached_rev


def _get_wikitext_and_revision(title: str, all_flag: str = "") -> tuple[str, str, bool]:
    """
    Fetch wikitext and revision ID.
    Tries live API first, then falls back to local cache.

    Returns:
        (wikitext, revision_id, from_cache)
    """
    mdwiki = MdwikiApi()
    source, revid, error = mdwiki.get_wikitext(title)


    from_cache = False
    if not source or not revid:
        # Fallback to local JSON mapping + cached file
        cached_source, revid = get_from_json(title, all_flag)
        from_cache = cached_source != ""

    # Add or update a title → revision mapping in the JSON index.
    if revid:
        add_title_revision(title, revid, all_flag)

    if not all_flag:
        full_text = source
        lead = get_lead_section(full_text)
        if lead and lead != full_text:
            source = expand_refs(lead, full_text)

    # run fix_wikitext as in the original PHP version
    fixer = WikitextFixerService(source, title)
    source = fixer.fix()

    return source, revid, from_cache


def _get_html(
    wikitext: str,
    file_html: Path,
    title: str,
    force_new: bool,
) -> tuple[str, bool]:
    """
    Convert wikitext to HTML with simple file caching.
    """
    from_cache = False
    # 1. check from cache
    if not force_new:
        cached = read_file(file_html)
        if cached:
            cached = remove_data_parsoid(cached)  # not in php
            return cached, True

    # fast return if wikitext is empty
    if not wikitext:
        return "", from_cache

    # convertWikitextToHtml
    transform = TransformApi()
    fixed = transform.convert(wikitext, title)
    html = fixed.get("result", "")

    # HTML conversion failed
    if not html:
        logger.error("HTML conversion failed for title: %s", title)
        return "", from_cache

    html = del_div_error(html)
    html = fix_link_red(html)

    if not html or html == wikitext:
        return "", from_cache

    # remove data parsoid and save file
    html_removed = remove_data_parsoid(html)
    write_file(file_html, html_removed)

    return html_removed, from_cache


def process_page(
    title: str,
    printetxt: str,
    force_new: bool,
    all_flag: str = "",
) -> Response:
    """
    Main entry point for the /new_html/ endpoint.
    """
    # 1. Get wikitext + revision
    wikitext, revision, text_from_cache = _get_wikitext_and_revision(title, all_flag)

    if not wikitext or not revision:
        response = jsonify(
            {
                "sourceLanguage": "en",
                "title": title,
                "revision": revision,
                "segmentedContent": "",
                "categories": [],
                "error_type": f"title:({title}) or revision:({revision}) not found",
                "error": "No content found!",
            }
        )
        response.status_code = 404
        return response

    file_dir = get_file_dir(revision, all_flag)
    file_wikitext = file_dir / "wikitext.txt"
    file_html = file_dir / "html.html"
    file_seg = file_dir / "seg.html"
    file_title = file_dir / "title.txt"

    # Apply temporary (empty) fix
    fixer = WikitextFixerService(wikitext, title)
    wikitext = fixer.fix()

    write_file(file_wikitext, wikitext)
    write_file(file_title, title)

    # Early exit for printetxt=wikitext
    if printetxt == "wikitext":
        response = Response(wikitext, mimetype="text/plain")
        return response

    # 2. Convert to HTML
    html, html_from_cache = _get_html(wikitext, file_html, title, force_new)

    if printetxt == "html":
        response = Response(html, mimetype="text/html")
        return response

    # 3. Convert to segments
    seg_text, seg_from_cache = get_segments(
        source_html=html,
        file_seg=file_seg,
        force_new=force_new,
    )

    if printetxt == "seg":
        response = Response(seg_text, mimetype="text/html")
        return response

    # Final JSON response
    data: dict[str, Any] = {
        "cache_data": {
            "wikitext": text_from_cache,
            "html": html_from_cache,
            "seg": seg_from_cache,
        },
        "sourceLanguage": "en",
        "title": title,
        "revision": revision,
        "segmentedContent": seg_text,
        "categories": [],
    }

    if not html:
        # Inconsistent error contract: When html is empty you still return HTTP 200 with error/error_type set,
        # but when seg is empty you return 404. Pick one convention (e.g. always 404 with an error envelope,
        # or always 200 with error fields) so clients can handle failures uniformly.

        data["error_type"] = "HTML_text:() is empty"
        data["error"] = "No content found"

    elif not seg_text:
        data["error_type"] = "seg_text:() is empty"
        data["error"] = "No content found"
        response = jsonify(data)
        # send request error code using status_code
        response.status_code = 404
        return response

    # Encode data as JSON with appropriate options
    response = jsonify(data)
    return response


__all__ = [
    "process_page",
]
