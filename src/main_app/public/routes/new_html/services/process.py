"""
Main processing logic for converting a page title into segmented content.
"""

import logging
from pathlib import Path

from flask import Response, jsonify, request

from ..config import JSON_FILE, JSON_FILE_ALL
from ..services.file_utils import read_file, write_file
from ..services.json_data import add_title_revision, get_title_revision
from ..services.mdwiki_api import MdwikiApiService
from ..services.segment_api import SegmentApiService
from ..services.transform_api import TransformApiService
from ..utils import get_content_type, get_file_dir, set_cors_headers

logger = logging.getLogger(__name__)


def fix_wikitext(text: str, title: str) -> str:
    """
    Temporary placeholder.
    Fixes and parsers are disabled for now.
    """
    return text


def get_wikitext_and_revision(title: str, all_flag: str = "") -> tuple[str, str, bool]:
    """
    Fetch wikitext and revision ID.
    Tries live API first, then falls back to local cache.

    Returns:
        (wikitext, revision_id, from_cache)
    """
    json_file = JSON_FILE_ALL if all_flag else JSON_FILE
    mdwiki = MdwikiApiService()

    result = mdwiki.get_wikitext(title)
    wikitext = result.get("source", "")
    revision = str(result.get("revid", ""))

    from_cache = False

    if not wikitext or not revision:
        # Fallback to local JSON mapping + cached file
        cached_rev = get_title_revision(title, json_file)
        if cached_rev:
            file_dir = get_file_dir(cached_rev, all_flag)
            cached_text = read_file(file_dir / "wikitext.txt")
            if cached_text:
                wikitext = cached_text
                revision = cached_rev
                from_cache = True

    if wikitext and revision:
        add_title_revision(title, revision, json_file)

    return wikitext, revision, from_cache


def get_html(wikitext: str, file_html: Path, title: str, force_new: bool) -> tuple[str, bool]:
    """
    Convert wikitext to HTML with simple file caching.
    """
    from_cache = False

    if not force_new:
        cached = read_file(file_html)
        if cached:
            return cached, True

    if not wikitext:
        return "", from_cache

    transform = TransformApiService()
    result = transform.convert(wikitext, title)

    html = result.get("result", "")
    if not html:
        logger.error(f"HTML conversion failed for title: {title}")
        return "", from_cache

    write_file(file_html, html)
    return html, from_cache


def get_segments(html: str, file_seg: Path) -> tuple[str, bool]:
    """
    Convert HTML to segments with simple file caching.
    """
    from_cache = False

    if "new" not in request.args:
        cached = read_file(file_seg)
        if cached:
            return cached, True

    if not html:
        return "", from_cache

    segment_service = SegmentApiService()
    result = segment_service.convert(html)

    seg = result.get("result", "")
    if not seg:
        return "", from_cache

    write_file(file_seg, seg)
    return seg, from_cache


def process_page() -> Response:
    """
    Main entry point for the /new_html/ endpoint.
    """
    title = request.args.get("title", "").strip()
    title = title[:1].upper() + title[1:] if title else ""

    printetxt = request.args.get("printetxt") or request.args.get("print") or ""
    force_new = "new" in request.args
    all_flag = request.args.get("all", "")

    # Special case: titles starting with "Video"
    if title.startswith("Video"):
        all_flag = "1"

    content_type = get_content_type(printetxt)

    if not title:
        response = jsonify({"error": "title is empty"})
        response.headers["Content-Type"] = "application/json"
        return set_cors_headers(response)

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
        return set_cors_headers(response)

    file_dir = get_file_dir(revision, all_flag)
    file_wikitext = file_dir / "wikitext.txt"
    file_html = file_dir / "html.html"
    file_seg = file_dir / "seg.html"
    file_title = file_dir / "title.txt"

    # Apply temporary (empty) fix
    wikitext = fix_wikitext(wikitext, title)

    write_file(file_wikitext, wikitext)
    write_file(file_title, title)

    # Early exit for printetxt=wikitext
    if printetxt == "wikitext":
        response = Response(wikitext, mimetype="text/plain")
        return set_cors_headers(response)

    # 2. Convert to HTML
    html, html_from_cache = get_html(wikitext, file_html, title, force_new)

    if printetxt == "html":
        response = Response(html, mimetype="text/html")
        return set_cors_headers(response)

    # 3. Convert to segments
    seg, seg_from_cache = get_segments(html, file_seg)

    if printetxt == "seg":
        response = Response(seg, mimetype="text/html")
        return set_cors_headers(response)

    # Final JSON response
    data = {
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
        data["error_type"] = "HTML_text is empty"
        data["error"] = "No content found"
    elif not seg:
        data["error_type"] = "SEG_text is empty"
        data["error"] = "No content found"
        response = jsonify(data)
        response.status_code = 404
        return set_cors_headers(response)

    response = jsonify(data)
    return set_cors_headers(response)


__all__ = [
    "fix_wikitext",
    "get_wikitext_and_revision",
    "get_html",
    "get_segments",
    "process_page",
]
