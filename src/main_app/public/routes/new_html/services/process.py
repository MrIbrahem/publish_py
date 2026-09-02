"""
Main processing pipeline for the new_html endpoint.

Pipeline:
1. Fetch wikitext + revision
2. WikitextFixerService.fix ← currently a no-op (TODO)
3. Convert wikitext → HTML (with cache)
4. Convert HTML → segments (with cache)
5. Return JSON envelope or raw content
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from flask import Request, Response, jsonify

from ...html_to_segments import process_html
from ..domain.fixes import WikitextFixerService
from .clients import MdwikiApi, TransformApi
from .html_utils import remove_data_parsoid
from .storage import (
    add_title_revision,
    get_title_revision,
    read_file,
    write_file,
)
from .utils import apply_cors_headers, get_file_dir

logger = logging.getLogger(__name__)


def get_wikitext_and_revision(title: str, all_flag: str = "") -> tuple[str, str, bool]:
    """
    Fetch wikitext and revision ID.
    Tries live API first, then falls back to local cache.

    Returns:
        (wikitext, revision_id, from_cache)
    """
    mdwiki = MdwikiApi()
    source, revid, error = mdwiki.get_wikitext(title)

    # TODO: In the original PHP version, fix_wikitext is also applied
    #       inside WikitextHandler before caching. Currently we only
    #       apply it later in process_page().

    from_cache = False

    if not source or not revid:
        # Fallback to local JSON mapping + cached file
        cached_rev = get_title_revision(title, all_flag)
        if cached_rev:
            file_dir = get_file_dir(cached_rev, all_flag)
            cached_text = read_file(file_dir / "wikitext.txt")
            if cached_text:
                source = cached_text
                revid = cached_rev
                from_cache = True

    if source and revid:
        add_title_revision(title, revid, all_flag)

    return source, revid, from_cache


def get_html(
    wikitext: str,
    file_html: Path,
    title: str,
    force_new: bool,
) -> tuple[str, bool]:
    """
    Convert wikitext to HTML with simple file caching.
    """
    from_cache = False

    if not force_new:
        cached = read_file(file_html)
        if cached:
            return remove_data_parsoid(cached), True

    if not wikitext:
        return "", from_cache

    transform = TransformApi()
    result = transform.convert(wikitext, title)

    html = result.get("result", "")
    if not html:
        logger.error("HTML conversion failed for title: %s", title)
        return "", from_cache

    html = remove_data_parsoid(html)
    write_file(file_html, html)
    return html, from_cache


def get_segments(html: str, file_seg: Path, force_new: bool) -> tuple[str, bool]:
    from_cache = False

    if not force_new:
        cached = read_file(file_seg)
        if cached:
            return remove_data_parsoid(cached), True

    if not html:
        return "", from_cache

    try:
        seg = process_html(html)
    except Exception as e:
        logger.error("Segment processing failed: %s", e)
        return "", from_cache

    if not seg:
        return "", from_cache

    # Normalize known empty messages (if any)
    if seg in (
        "Content for translate is not given or is empty",
        "Sectionwrap: Attempting to remove a non-section tag: undefined",
    ):
        return "", from_cache

    seg = remove_data_parsoid(seg)
    write_file(file_seg, seg)
    return seg, from_cache


def process_page(request: Request) -> Response:
    """
    Main entry point for the /new_html/ endpoint.
    """
    title = (request.args.get("title") or "").strip()
    if title:
        title = title[0].upper() + title[1:]

    printetxt = request.args.get("printetxt") or request.args.get("print") or ""
    force_new = "new" in request.args
    all_flag = request.args.get("all", "")

    # Special case: titles starting with "Video"
    if title.startswith("Video"):
        all_flag = "1"

    if not title:
        response = jsonify({"error": "title is empty"})
        return apply_cors_headers(response, request)

    # 1. Get wikitext + revision
    wikitext, revision, text_from_cache = get_wikitext_and_revision(title, all_flag)

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
        return apply_cors_headers(response, request)

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
        return apply_cors_headers(response, request)

    # 2. Convert to HTML
    html, html_from_cache = get_html(wikitext, file_html, title, force_new)

    if printetxt == "html":
        response = Response(html, mimetype="text/html")
        return apply_cors_headers(response, request)

    # 3. Convert to segments
    seg, seg_from_cache = get_segments(html, file_seg, force_new)

    if printetxt == "seg":
        response = Response(seg, mimetype="text/html")
        return apply_cors_headers(response, request)

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
        "segmentedContent": seg,
        "categories": [],
    }

    if not html:
        # Inconsistent error contract: When html is empty you still return HTTP 200 with error/error_type set,
        # but when seg is empty you return 404. Pick one convention (e.g. always 404 with an error envelope,
        # or always 200 with error fields) so clients can handle failures uniformly.

        data["error_type"] = "HTML_text is empty"
        data["error"] = "No content found"

    elif not seg:
        data["error_type"] = "SEG_text is empty"
        data["error"] = "No content found"
        response = jsonify(data)
        response.status_code = 404
        return apply_cors_headers(response, request)

    response = jsonify(data)
    return apply_cors_headers(response, request)
