"""
Route definitions for the new_html blueprint.
"""

from __future__ import annotations

import re

from flask import Blueprint, Response, abort, jsonify, render_template, request

from ....config.main_settings import get_settings
from ....services.core.cors import check_cors
from .services.html_utils import remove_data_parsoid
from .services.process import process_page
from .services.storage import list_revisions, read_file


class NewHtmlRoutes:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:
        routes = [
            ("/index", ["GET"], self.index),
            ("/", ["GET"], check_cors(self.main)),
            ("/check", ["GET"], check_cors(self.check)),
            ("/open", ["GET"], check_cors(self.open_file)),
            ("/revisions_api", ["GET"], check_cors(self.revisions_api)),
        ]
        for rule, methods, target in routes:
            self.bp.route(rule, methods=methods)(target)

    def index(self) -> str:
        return render_template(
            "new_text/revisions.html",
        )

    def main(self) -> Response:
        """
        Main API endpoint.
        Example: /new_html/?title=Trifluoperazine
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
            return jsonify({"error": "title is empty"})

        return process_page(title, printetxt, force_new, all_flag)

    def check(self) -> Response:
        """
        Check whether both seg.html and html.html exist for a revision.
        Example: /new_html/check?revid=123456
        """
        revid = self._get_revision_id()

        if not revid:
            response = Response("false", mimetype="text/plain")
            return response

        settings = get_settings()
        dir_path = settings.new_html.revisions_dir / revid

        if not dir_path.is_dir():
            response = Response("false", mimetype="text/plain")
            return response

        seg_exists = (dir_path / "seg.html").is_file()
        html_exists = (dir_path / "html.html").is_file()

        result = "true" if (seg_exists and html_exists) else "false"
        response = Response(result, mimetype="text/plain")
        return response

    def open_file(self) -> Response:
        """
        Serve a cached file (wikitext.txt | html.html | seg.html).
        Example: /new_html/open?revid=123456&file=html.html
        """
        revid = self._get_revision_id()
        file_name = (request.args.get("file") or "").strip()

        if not revid:
            abort(400, description="Invalid revision ID")

        allowed_files = {"wikitext.txt", "html.html", "seg.html"}
        if file_name not in allowed_files:
            abort(400, description="Invalid file parameter")

        settings = get_settings()
        file_path = settings.new_html.revisions_dir / revid / file_name

        if not file_path.is_file():
            abort(404, description="File not found")

        content = read_file(file_path)

        if file_name in {"html.html", "seg.html"}:
            content = remove_data_parsoid(content)

        mimetype = "text/plain" if file_name == "wikitext.txt" else "text/html"
        response = Response(content, mimetype=mimetype)
        return response

    def revisions_api(self) -> Response:
        """
        Return list of cached revisions for the dashboard.
        """
        results = list_revisions()
        response = jsonify({"results": results})
        return response

    def _get_revision_id(self) -> str | None:
        revid = (request.args.get("revid") or "").strip()

        if not revid:
            return None

        # Security: only allow specific revision patterns
        if not re.match(r"^\d+(_all)?$", revid):
            return None

        return revid
