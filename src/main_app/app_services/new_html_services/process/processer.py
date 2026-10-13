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

from ....services.clients import HttpClient
from ..clients import MdwikiApi, TransformApiService
from ..storage import Storage
from ..utils import FileUtils, HtmlUtils
from ..wikitext_fixes import WikitextFixerService
from .html_service import WikitextToHtmlService
from .mapping import PageRequest, PageResult
from .process_seg import HtmlToSegmentsService

logger = logging.getLogger(__name__)


class PagePipelineService:
    """Orchestrates: fetch wikitext -> fix -> HTML -> segments.

    This file handles HTTP requests to generate page content from MDWiki.
    It orchestrates the full pipeline: fetching wikitext, applying fixes,
    converting to HTML, and segmenting the content.

    Request parameters:
    - title: Page title to process
    - new: Force reqeneration of cached content
    - all: Use 'all' data file for Video pages
    - printetxt: Output format (wikitext|html|seg)
    - print: Alias for printetxt
    """

    def __init__(
        self,
        http_client: HttpClient | None = None,
    ) -> None:
        """Initialize the checker with an HTTP client instance."""
        self.http_client = http_client or HttpClient()
        self.mdwiki_api = MdwikiApi(self.http_client)
        self.transform = TransformApiService(self.http_client)
        self.fixer = WikitextFixerService(self.http_client)

    def _from_local_cache(self, title: str, all_flag: str) -> tuple[str, str]:
        """ """
        cached_rev = Storage.get_title_revision(title, all_flag)

        if not cached_rev or not cached_rev.isdigit():
            return "", ""

        file_dir = FileUtils.get_file_dir(cached_rev, all_flag)
        if not file_dir.is_dir():
            return "", ""

        cached_text = FileUtils.read_file(file_dir / "wikitext.txt")

        if not cached_text:
            return "", ""

        return cached_text, cached_rev

    def _get_wikitext_and_revision(self, title: str, all_flag: str = "") -> tuple[str, str, bool]:
        """
        Fetch wikitext and revision ID.
        Tries live API first, then falls back to local cache.

        Returns:
            (wikitext, revision_id, from_cache)
        """
        source, revid, error = self.mdwiki_api.get_wikitext(title)

        from_cache = False
        if not source or not revid:
            # Fallback to local JSON mapping + cached file
            cached_source, revid = self._from_local_cache(title, all_flag)
            from_cache = cached_source != ""

        # Add or update a title → revision mapping in the JSON index.
        if revid:
            Storage.add_title_revision(title, revid, all_flag)

        # run fix_wikitext as in the original PHP version
        source = self.fixer.run(source, title, all_flag=bool(all_flag))

        return source, revid, from_cache

    def _get_html(
        self,
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
            cached = FileUtils.read_file(file_html)
            if cached:
                cached = HtmlUtils.remove_data_parsoid(cached)  # not in php
                return cached, True

        # fast return if wikitext is empty
        if not wikitext:
            return "", from_cache

        # TransformApiService.convert()
        fixed = self.transform.convert(wikitext, title)
        html = fixed.get("result", "")

        # HTML conversion failed
        if not html:
            logger.error("HTML conversion failed for title: %s", title)
            return "", from_cache

        html = HtmlUtils.del_div_error(html)
        html = HtmlUtils.fix_link_red(html)

        if not html or html == wikitext:
            return "", from_cache

        # remove data parsoid and save file
        html_removed = HtmlUtils.remove_data_parsoid(html)
        FileUtils.write_file(file_html, html_removed)

        return html_removed, from_cache

    def process_page(
        self,
        title: str,
        printetxt: str,
        force_new: bool,
        all_flag: str = "",
    ) -> Response:
        """
        Main entry point for the /new_html/ endpoint.
        """
        # 1. Get wikitext + revision
        wikitext, revision, text_from_cache = self._get_wikitext_and_revision(title, all_flag)

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

        file_dir = FileUtils.get_file_dir(revision, all_flag)
        file_wikitext = file_dir / "wikitext.txt"
        file_html = file_dir / "html.html"
        file_seg = file_dir / "seg.html"
        file_title = file_dir / "title.txt"

        # Apply temporary (empty) fix
        fixer = WikitextFixerService()
        wikitext = fixer.fix(wikitext, title)

        FileUtils.write_file(file_wikitext, wikitext)
        FileUtils.write_file(file_title, title)

        # Early exit for printetxt=wikitext
        if printetxt == "wikitext":
            response = Response(wikitext, mimetype="text/plain")
            return response

        # 2. Convert to HTML
        html, html_from_cache = self._get_html(wikitext, file_html, title, force_new)

        if printetxt == "html":
            response = Response(html, mimetype="text/html")
            return response

        # 3. Convert to segments
        seg, seg_from_cache = HtmlToSegmentsService().get_segments(
            source_html=html,
            file_seg=file_seg,
            force_new=force_new,
        )
        FileUtils.write_file(file_seg, seg)

        if printetxt == "seg":
            response = Response(seg, mimetype="text/html")
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
            "segmentedContent": seg,
            "categories": [],
        }

        if not html:
            # Inconsistent error contract: When html is empty you still return HTTP 200 with error/error_type set,
            # but when seg is empty you return 404. Pick one convention (e.g. always 404 with an error envelope,
            # or always 200 with error fields) so clients can handle failures uniformly.

            data["error_type"] = "HTML_text:() is empty"
            data["error"] = "No content found"

        elif not seg:
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
    "PagePipelineService",
]
