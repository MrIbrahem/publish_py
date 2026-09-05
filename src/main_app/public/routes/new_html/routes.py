"""
Route definitions for the new_html blueprint.
"""

from __future__ import annotations

import re

from flask import Blueprint, Response, abort, flash, jsonify, render_template, request

from ....config.main_settings import settings
from ....services.core.cors import check_cors
from .services.html_utils import remove_data_parsoid
from .services.process import WikitextFixerService, process_page
from .services.storage import list_revisions, read_file


class NewHtmlRoutes:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self.revisions_dir = settings.new_html.revisions_dir
        self._setup_routes()

    def _setup_routes(self) -> None:
        routes = [
            ("/fix", ["GET", "POST"], self.fix),
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
            "new_html/revisions.html",
        )

    def fix(self) -> str:
        """
        Wikitext fixing test page.

        Provides a web interface for testing the wikitext fixing functionality.
        Users can input wikitext and a title, and see the results of applying
        various fixes.
        """
        title = ""
        wikitext = ""

        def render(title: str | None = "", wikitext: str | None = "") -> str:
            return render_template(
                "new_html/fix.html",
                wikitext=wikitext,
                title=title,
            )

        if request.method != "POST":
            return render()

        title = request.form.get("title")
        wikitext = request.form.get("text")

        if not title:
            flash("Please enter a title", "danger")

        if not wikitext:
            flash("Please enter wikitext", "danger")

        if not title or not wikitext:
            return render(title, wikitext)

        fixer = WikitextFixerService()

        changed_text = fixer.fix(wikitext, title)
        if changed_text != wikitext:
            flash("Changes made.", "success")
            return render(title, changed_text)

        flash("No changes made.", "warning")
        return render(title, wikitext)

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

        return process_page(
            title=title,
            printetxt=printetxt,
            force_new=force_new,
            all_flag=all_flag,
        )

    def check(self) -> Response:
        """
        Check whether both seg.html and html.html exist for a revision.
        Example: /new_html/check?revid=123456
        """
        revid = self._get_revision_id()

        if not revid:
            response = Response("false", mimetype="text/plain")
            return response

        dir_path = self.revisions_dir / revid

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

        file_path = self.revisions_dir / revid / file_name

        if not file_path.is_file():
            abort(404, description="File not found")

        content = read_file(file_path)

        mimetype = "text/plain" if file_name == "wikitext.txt" else "text/html"

        # if file_name in {"html.html", "seg.html"}:
        if mimetype == "text/html":
            content = remove_data_parsoid(content)

        response = Response(content, mimetype=mimetype)
        return response

    def revisions_api(self) -> Response:
        """
        Return list of cached revisions for the dashboard.
        """

        results = list_revisions(self.revisions_dir)
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
