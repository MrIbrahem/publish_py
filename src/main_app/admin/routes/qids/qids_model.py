"""s
"""

from __future__ import annotations

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from ....db.models import QidOthersRecord, QidRecord


logger = logging.getLogger(__name__)

VALID_DIS = {"all", "empty", "duplicate"}


def is_valid(qid_id: int | bool, qid: str, title: str, existing_by_qid, existing_by_title) -> bool:
    # existing_by_qid = _service.get_by_qid(qid)
    if existing_by_qid:
        if qid_id and existing_by_qid.id != qid_id:
            flash(
                f"Qid:({qid}) already used in database with id:({existing_by_qid.id}).",
                "danger",
            )
            return False
        if not qid_id and existing_by_qid.title and existing_by_qid.title != title:
            flash(
                f"Qid:({qid}) already used in database with title:({existing_by_qid.title}).",
                "danger",
            )
            return False

    # Validation 2: title already used in DB by a different id (or by a row
    # with a non-empty different qid when inserting)
    # existing_by_title = _service.get_by_title(title)
    if existing_by_title:
        if qid_id and existing_by_title.id != qid_id:
            flash(
                f"Title:({title}) already used in database with qid:"
                f"({existing_by_title.qid}), new qid:({qid})",
                "danger",
            )
            return False
        if not qid_id and existing_by_title.qid and existing_by_title.qid != qid:
            flash(
                f"Title:({title}) already used in database with qid:"
                f"({existing_by_title.qid}), new qid:({qid})",
                "danger",
            )
            return False

    return True


class QidsModel:
    def __init__(
        self,
        endpoint: str,
        url_prefix: str,
        title_label: str,
        service,
    ):
        self.bp = Blueprint(endpoint, __name__, url_prefix=url_prefix)
        self.endpoint = endpoint
        self.title_label = title_label
        self.service = service
        self._setup_routes()

    def is_valid(self, qid_id: int | bool, qid: str, title: str) -> bool:
        existing_by_qid = self.service.get_by_qid(qid)
        existing_by_title = self.service.get_by_title(title)
        return is_valid(qid_id, qid, title, existing_by_qid, existing_by_title)

    def _setup_routes(self):
        @self.bp.route("/", methods=["GET"])
        def index() -> str:
            """List of rows with optional filter (all / empty / duplicate)."""
            dis = request.args.get("dis", "all")
            if dis not in VALID_DIS:
                dis = "all"

            try:
                rows = self.service.list_records(dis=dis)
            except Exception:
                logger.exception("Failed to list qids rows dis=%r", dis)
                rows = []

            return render_template(
                "admins/qids/index.html",
                rows=rows,
                dis=dis,
                qid_table=self.endpoint,
                title_label=self.title_label,
                index_endpoint=f"admin.{self.endpoint}.index",
                edit_endpoint=f"admin.{self.endpoint}.edit",
                post_endpoint=f"admin.{self.endpoint}.edit_post",

                add_endpoint=f"admin.{self.endpoint}.add",
            )

        @self.bp.route("/edit", methods=["GET"])
        def edit() -> str:
            """Render the add/edit popup for a single row."""
            qid_id = None
            qid_id_raw = request.args.get("id", "")
            try:
                qid_id = int(qid_id_raw)
            except (ValueError, TypeError):
                flash(f"Invalid ID: {qid_id_raw}", "danger")
                return redirect(url_for("admin.edit_done"))

            record: QidRecord | QidOthersRecord = self.service.get_by_id(qid_id)
            if not record:
                flash(f"Record not found. id={qid_id}", "danger")
                return redirect(url_for("admin.edit_done"))

            return render_template(
                "admins/qids/edit.html",
                id=qid_id,
                title=record.title,
                qid=record.qid,
                qid_table=self.endpoint,
                post_endpoint=f"admin.{self.endpoint}.edit_post",
            )

        @self.bp.route("/add", methods=["GET"])
        def add() -> str:
            """Render the add popup for a single qids row."""
            return render_template(
                "admins/qids/edit.html",
                new=1,
                title="",
                qid="",
                qid_table=self.endpoint,
                post_endpoint=f"admin.{self.endpoint}.add_post",
            )

        @self.bp.route("/", methods=["POST"])
        def edit_post() -> ResponseReturnValue:
            """update a row."""
            qid_id_raw = (request.form.get("id") or "").strip()
            title = (request.form.get("title") or "").strip()
            qid = (request.form.get("qid") or "").strip()

            edit_done_ep = redirect(url_for("admin.edit_done"))

            qid_id: int | None = None
            try:
                qid_id = int(qid_id_raw)
            except ValueError:
                flash(f"Invalid id: {qid_id_raw}", "danger")
                return edit_done_ep

            edit_redirect_to = redirect(url_for(f"admin.{self.endpoint}.edit", id=qid_id))

            if not title:
                flash(f"Title is required. qid=({qid})", "danger")
                return edit_redirect_to

            if not qid:
                flash(f"Qid is required. title=({title})", "danger")
                return edit_redirect_to

            try:
                if not self.is_valid(qid_id, qid, title):
                    return edit_redirect_to

            except Exception:
                logger.exception("Failed to save qids row id=%r title=%r qid=%r", qid_id, title, qid)
                flash(f"Failed to check data for title: {title}, Qid: {qid}.", "danger")
                return edit_redirect_to

            try:
                ok = self.service.update(qid_id, title, qid)
            except Exception:
                logger.exception("Failed to save row id=%r title=%r qid=%r", qid_id, title, qid)
                ok = False

            if ok:
                flash(f"Data saved successfully for title: {title}, Qid: {qid}.", "success")
                return edit_done_ep

            flash(f"Failed to save data for title: {title}, Qid: {qid}.", "danger")

            return edit_redirect_to

        @self.bp.route("/add", methods=["POST"])
        def add_post() -> ResponseReturnValue:
            """Insert a qid row"""
            title = (request.form.get("title") or "").strip()
            qid = (request.form.get("qid") or "").strip()

            edit_done_ep = redirect(url_for("admin.edit_done"))

            edit_redirect_to = redirect(url_for(f"admin.{self.endpoint}.add"))

            if not title:
                flash(f"Title is required. qid=({qid})", "danger")
                return edit_redirect_to

            if not qid:
                flash(f"Qid is required. title=({title})", "danger")
                return edit_redirect_to

            try:
                if not self.is_valid(False, qid, title):
                    return edit_redirect_to

            except Exception:
                logger.exception("Failed to save qids row title=%r qid=%r", title, qid)
                flash(f"Failed to check data for title: {title}, Qid: {qid}.", "danger")
                return edit_redirect_to

            try:
                ok = self.service.insert(title, qid)
            except Exception:
                logger.exception("Failed to save row title=%r qid=%r", title, qid)
                ok = False

            if ok:
                flash(f"Data saved successfully for title: {title}, Qid: {qid}.", "success")
                return edit_done_ep

            flash(f"Failed to save data for title: {title}, Qid: {qid}.", "danger")

            return edit_redirect_to
