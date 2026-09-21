"""
Route definitions for the new_html blueprint.
"""

from __future__ import annotations

import re

from flask import Blueprint, Response, abort, flash, jsonify, render_template, request
from flask.views import MethodView

from ...config.main_settings import app_settings
from ...services.core.cors import check_cors
from ...services.new_html_services import (
    WikitextFixerService,
    list_revisions,
    process_page,
    read_file,
    remove_data_parsoid,
)


def _get_revisions_dir():
    """Return the configured directory holding cached revisions."""
    return app_settings.new_html.revisions_dir


def _get_revision_id() -> str | None:
    """Read and validate the ``revid`` query parameter.

    Only plain digits with an optional ``_all`` suffix are accepted so the
    value can never escape the revisions directory.
    """
    revid = (request.args.get("revid") or "").strip()

    if not revid:
        return None

    # Security: only allow specific revision patterns
    if not re.match(r"^\d+(_all)?$", revid):
        return None

    return revid


class NewHtmlFixView(MethodView):
    """Wikitext fixing test page."""

    def get(self) -> str:
        """Render the empty fixing form."""
        return self._render()

    def post(self) -> str:
        """Run the wikitext fixer over the submitted title/text."""
        title = request.form.get("title", type=str)
        wikitext = request.form.get("text", type=str)
        lead_only = request.form.get("lead_only", type=bool, default=True)

        if not title:
            flash("Please enter a title", "danger")

        if not wikitext:
            flash("Please enter wikitext", "danger")

        if not title or not wikitext:
            return self._render(title, wikitext)

        fixer = WikitextFixerService()

        changed_text = fixer.run(wikitext, title, all_flag=not (lead_only))

        if changed_text != wikitext:
            flash("Changes made.", "success")
            return self._render(title, changed_text)

        flash("No changes made.", "warning")
        return self._render(title, wikitext)

    @staticmethod
    def _render(title: str | None = "", wikitext: str | None = "") -> str:
        """Render the fix page with the given title and wikitext."""
        return render_template(
            "new_html/fix.html",
            wikitext=wikitext,
            title=title,
        )


class NewHtmlIndexView(MethodView):
    """Render the revisions dashboard page."""

    def get(self) -> str:
        """Render the revisions listing page."""
        return render_template(
            "new_html/revisions.html",
        )


class NewHtmlMainView(MethodView):
    """Main API endpoint producing segment-ready HTML for a title."""

    decorators = [check_cors]

    def get(self) -> Response:
        """Process the requested title.

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


class NewHtmlCheckView(MethodView):
    """Check whether both seg.html and html.html exist for a revision."""

    decorators = [check_cors]

    def get(self) -> Response:
        """Return ``true``/``false`` as plain text.

        Example: /new_html/check?revid=123456
        """
        revid = _get_revision_id()

        if not revid:
            response = Response("false", mimetype="text/plain")
            return response

        dir_path = _get_revisions_dir() / revid

        if not dir_path.is_dir():
            response = Response("false", mimetype="text/plain")
            return response

        seg_exists = (dir_path / "seg.html").is_file()
        html_exists = (dir_path / "html.html").is_file()

        result = "true" if (seg_exists and html_exists) else "false"
        response = Response(result, mimetype="text/plain")
        return response


class NewHtmlOpenFileView(MethodView):
    """Serve a cached file (wikitext.txt | html.html | seg.html)."""

    decorators = [check_cors]

    def get(self) -> Response:
        """Stream the requested revision file.

        Example: /new_html/open?revid=123456&file=html.html
        """
        revid = _get_revision_id()
        file_name = (request.args.get("file") or "").strip()

        if not revid:
            abort(400, description="Invalid revision ID")

        allowed_files = {"wikitext.txt", "html.html", "seg.html"}
        if file_name not in allowed_files:
            abort(400, description="Invalid file parameter")

        file_path = _get_revisions_dir() / revid / file_name

        if not file_path.is_file():
            abort(404, description="File not found")

        content = read_file(file_path)

        mimetype = "text/plain" if file_name == "wikitext.txt" else "text/html"

        # if file_name in {"html.html", "seg.html"}:
        if mimetype == "text/html":
            content = remove_data_parsoid(content)

        response = Response(content, mimetype=mimetype)
        return response


class NewHtmlRevisionsApiView(MethodView):
    """Return the list of cached revisions for the dashboard."""

    decorators = [check_cors]

    def get(self) -> Response:
        """Return the revision listing as JSON."""
        results = list_revisions(_get_revisions_dir())
        response = jsonify({"results": results})
        return response


class NewHtmlRoutes:
    """Registrar for the new_html views."""

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register the new_html endpoints on the blueprint."""
        bp.add_url_rule("/fix", view_func=NewHtmlFixView.as_view("fix"), methods=["GET", "POST"])
        bp.add_url_rule("/index", view_func=NewHtmlIndexView.as_view("index"), methods=["GET"])
        bp.add_url_rule("/", view_func=NewHtmlMainView.as_view("main"), methods=["GET"])
        bp.add_url_rule("/check", view_func=NewHtmlCheckView.as_view("check"), methods=["GET"])
        bp.add_url_rule("/open", view_func=NewHtmlOpenFileView.as_view("open_file"), methods=["GET"])
        bp.add_url_rule("/revisions_api", view_func=NewHtmlRevisionsApiView.as_view("revisions_api"), methods=["GET"])


__all__ = [
    "NewHtmlRoutes",
]
