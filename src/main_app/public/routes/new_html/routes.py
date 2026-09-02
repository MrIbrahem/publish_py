"""
Route definitions for the new_html Blueprint.
"""

import logging

from flask import Blueprint, Response, abort, jsonify, request

from .config import REVISIONS_PATH
from .services.file_utils import read_file
from .services.process import process_page
from .utils import set_cors_headers

logger = logging.getLogger(__name__)


class NewHtmlRoutes:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:
        routes = [
            ("/", ["GET"], self.main),
            ("/check", ["GET"], self.check),
            ("/open", ["GET"], self.open_file),
            ("/revisions_api", ["GET"], self.revisions_api),
        ]
        for rule, methods, target in routes:
            self.bp.route(rule, methods=methods)(target)

    def main(self):
        """
        Main API endpoint.
        Example: /new_html/?title=Trifluoperazine
        """
        return process_page()

    def check(self):
        """
        Check whether both seg.html and html.html exist for a revision.
        Example: /new_html/check?revid=123456
        """
        revid = request.args.get("revid", "").strip()

        if not revid or not revid.isdigit():
            return "false"

        dir_path = REVISIONS_PATH / revid
        if not dir_path.is_dir():
            return "false"

        seg_exists = (dir_path / "seg.html").is_file()
        html_exists = (dir_path / "html.html").is_file()

        return "true" if (seg_exists and html_exists) else "false"

    def open_file(self):
        """
        Serve a cached file (wikitext.txt | html.html | seg.html).
        Example: /new_html/open?revid=123456&file=html.html
        """
        revid = request.args.get("revid", "").strip()
        file_name = request.args.get("file", "").strip()

        # Basic security: only allow specific patterns
        import re

        if not re.match(r"^\d+(_all)?$", revid):
            abort(400, description="Invalid revision ID")

        allowed_files = {"wikitext.txt", "html.html", "seg.html"}
        if file_name not in allowed_files:
            abort(400, description="Invalid file parameter")

        file_path = REVISIONS_PATH / revid / file_name
        if not file_path.is_file():
            abort(404, description="File not found")

        content = read_file(file_path)
        mimetype = "text/plain" if file_name == "wikitext.txt" else "text/html"

        response = Response(content, mimetype=mimetype)
        return set_cors_headers(response)

    def revisions_api(self):
        """
        Return list of cached revisions for the dashboard.
        """
        from datetime import datetime

        dirs = [d for d in REVISIONS_PATH.iterdir() if d.is_dir()]
        # Sort by last modification time (newest first)
        dirs.sort(
            key=lambda d: (d / "wikitext.txt").stat().st_mtime if (d / "wikitext.txt").exists() else d.stat().st_mtime,
            reverse=True,
        )

        results = []
        for idx, dir_path in enumerate(dirs, start=1):
            dir_name = dir_path.name
            oldid = dir_name.replace("_all", "")

            wikitext_file = dir_path / "wikitext.txt"
            last_modified = (
                datetime.fromtimestamp(wikitext_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                if wikitext_file.exists()
                else datetime.fromtimestamp(dir_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            )

            title_file = dir_path / "title.txt"
            title = read_file(title_file).replace("_", " ") if title_file.exists() else ""

            results.append(
                {
                    "number": idx,
                    "lastModified": last_modified,
                    "title": title,
                    "dir_path": dir_name,
                    "oldid_number": oldid,
                    "wikitext_exists": (dir_path / "wikitext.txt").exists(),
                    "html_exists": (dir_path / "html.html").exists(),
                    "seg_exists": (dir_path / "seg.html").exists(),
                }
            )

        response = jsonify({"results": results})
        return set_cors_headers(response)


__all__ = [
    "NewHtmlRoutes",
]
