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

from ....services.clients import HttpClient
from ..clients import MdwikiRestFallbackService
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
        fixer: WikitextFixerService | None = None,
        html_service: WikitextToHtmlService | None = None,
        html_seg_service: HtmlToSegmentsService | None = None,
    ) -> None:
        """Initialize the checker with an HTTP client instance."""
        self.http_client = http_client or HttpClient()
        self.mdwiki_api = MdwikiRestFallbackService(self.http_client)
        self.fixer = fixer or WikitextFixerService(self.http_client)
        self.html_service = html_service or WikitextToHtmlService()
        self.html_seg_service = html_seg_service or HtmlToSegmentsService()

    # ------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------

    def process(self, req: PageRequest) -> PageResult:
        """Process the page request through the pipeline."""
        cache = {"wikitext": False, "html": False, "seg": False}

        # 1. Get wikitext + revision
        wikitext, revision, cache["wikitext"] = self._fetch_wikitext(req)

        if not wikitext or not revision:
            return self._not_found(req.title, revision)

        # Apply temporary (empty) fix
        wikitext = self.fixer.fix(wikitext, req.title)

        # Early exit for printetxt=wikitext
        if req.format == PageRequest.FORMAT_WIKITEXT:
            return PageResult.text(PageRequest.FORMAT_WIKITEXT, wikitext)

        dir_path = FileUtils.get_file_dir(revision, req.all)
        file_wikitext = dir_path / "wikitext.txt"
        file_html = dir_path / "html.html"
        file_title = dir_path / "title.txt"
        file_seg = dir_path / "seg.html"

        FileUtils.write_file(file_wikitext, wikitext)
        FileUtils.write_file(file_title, req.title)

        # 2. Convert to HTML
        try:
            html, cache["html"] = self._build_html(wikitext, file_html, req)
        except Exception as e:
            logging.error(f"HTML generation failed for title: {req.title}. Error: {e}")
            return PageResult.json(500, {"error": "Failed to generate HTML content"})

        if req.format == PageRequest.FORMAT_HTML:
            return PageResult.text(PageRequest.FORMAT_HTML, html)

        # Final JSON response
        data = self._base_data(req.title, revision, cache)

        if not html:
            # Inconsistent error contract: When html is empty you still return HTTP 200 with error/error_type set,
            # but when seg is empty you return 404. Pick one convention (e.g. always 404 with an error envelope,
            # or always 200 with error fields) so clients can handle failures uniformly.

            data["error_type"] = "HTML_text:() is empty"
            data["error"] = "No content found"
            return PageResult.json(200, data)

        # 3. Convert to segments
        seg, cache["seg"] = self._build_segments(html, file_seg, req.new)

        if req.format == PageRequest.FORMAT_SEG:
            return PageResult.text(PageRequest.FORMAT_SEG, seg)

        data["cache_data"] = cache
        data["segmentedContent"] = seg

        if not seg:
            # send request error code using http response code equivalent
            data["error_type"] = "seg_text:() is empty"
            data["error"] = "No content found"
            return PageResult.json(404, data)

        return PageResult.json(200, data)

    # ------------------------------------------------------------
    # Steps
    # ------------------------------------------------------------

    def _fetch_wikitext(self, req: PageRequest) -> tuple[str, str, bool]:
        """
        Fetch wikitext and revision ID.
        Tries live API first, then falls back to local cache.

        Returns:
            (wikitext, revision_id, from_cache)
        """
        data = self.mdwiki_api.get_wikitext(req.title)
        source = data["source"]
        revid = data["revid"]
        error = data["error"]

        from_cache = False
        if not source or not revid:
            # Fallback to local JSON mapping + cached file
            cached_source, revid = self._from_local_cache(req.title, req.all)
            from_cache = cached_source != ""
            source = source or cached_source

        # Add or update a title → revision mapping in the JSON index.
        if revid:
            Storage.add_title_revision(req.title, revid, req.all)

        # run fix_wikitext as in the original PHP version
        source = self.fixer.run(source, req.title, all_flag=bool(req.all))

        return source, revid, from_cache

    def _from_local_cache(self, title: str, all_flag: bool = False) -> tuple[str, str]:
        """Get wikitext and revision ID from cached JSON data."""
        revid = Storage.get_title_revision(title, all_flag)

        if not revid or not str(revid).isdigit():
            return "", ""

        dir_path = FileUtils.get_file_dir(revid, all_flag)

        if not dir_path.is_dir():
            return "", ""

        cached_text = FileUtils.read_file(dir_path / "wikitext.txt")

        if not cached_text:
            return "", ""

        return cached_text, revid

    def _build_html(self, wikitext: str, file_html: Path, req: PageRequest) -> tuple[str, bool]:
        """Convert wikitext to HTML with caching support."""
        html, from_cache = self.html_service.convert_with_cache(wikitext, file_html, req.title, req.new)

        html = HtmlUtils.fix_html(html)

        if html == wikitext:
            html = ""

        return html, from_cache

    def _build_segments(self, html: str, file_seg: Path, force_new: bool) -> tuple[str, bool]:
        """Convert HTML to segments with caching support."""
        seg, from_cache = self.html_seg_service.get_segments(
            source_html=html,
            file_path=file_seg,
            force_new=force_new,
        )
        seg = HtmlUtils.fix_seg(seg)

        if not from_cache:
            FileUtils.write_file(file_seg, seg)

        return seg, from_cache

    # ------------------------------------------------------------
    # Result builders
    # ------------------------------------------------------------

    def _base_data(self, title: str, revision: str, cache: dict[str, bool]) -> dict[str, Any]:
        """Build base response data array."""
        return {
            "cache_data": cache,
            "sourceLanguage": "en",
            "title": title,
            "revision": revision,
            "segmentedContent": "",
            "categories": [],
        }

    def _not_found(self, title: str, revision: str) -> PageResult:
        """Build not found response."""
        return PageResult.json(
            404,
            {
                "sourceLanguage": "en",
                "title": title,
                "revision": revision,
                "segmentedContent": "",
                "categories": [],
                "error_type": f"title:({title}) or revision:({revision}) not found",
                "error": "No content found!",
            },
        )


__all__ = [
    "PagePipelineService",
]
