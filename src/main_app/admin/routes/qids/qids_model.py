"""Shared MethodViews and route handler logic for QID management tables."""

from __future__ import annotations

import logging
from typing import TypeVar

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from flask.views import MethodView
from werkzeug.wrappers.response import Response

from ....database.models import QidOthersRecord, QidRecord
from ....database.services import QidOthersService, QidService
from ...decorators import admin_required

logger = logging.getLogger(__name__)

VALID_DIS = {"all", "empty", "duplicate"}

QidsModel = TypeVar("QidsModel", bound=QidOthersRecord | QidRecord)


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
        msg = f"Title:({title}) already used in database with qid:({existing_by_title.qid}), new qid:({qid})"

        if qid_id and existing_by_title.id != qid_id:
            flash(msg, "danger")
            return False

        if not qid_id and existing_by_title.qid and existing_by_title.qid != qid:
            flash(msg, "danger")
            return False

    return True


class BaseQidView(MethodView):
    """Base view class providing shared service and validation utilities."""

    decorators = [admin_required]

    def __init__(
        self,
        endpoint: str,
        title_label: str,
        service: QidService | QidOthersService,
    ) -> None:
        self.endpoint = endpoint
        self.title_label = title_label
        self.service = service

    def is_valid_qid(self, qid_id: int | bool, qid: str, title: str) -> bool:
        """Validate QID uniqueness across title and qid columns."""
        existing_by_qid = self.service.get_by_qid(qid)
        existing_by_title = self.service.get_by_title(title)
        return is_valid(qid_id, qid, title, existing_by_qid, existing_by_title)


class QidIndexView(BaseQidView):
    """View to handle listing QID records with optional filtering."""

    def get(self) -> str:
        """Render list of QID records."""
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
            index_endpoint=f"adminpanel.{self.endpoint}.index",
            edit_endpoint=f"adminpanel.{self.endpoint}.edit",
            post_endpoint=f"adminpanel.{self.endpoint}.edit",
            add_endpoint=f"adminpanel.{self.endpoint}.add",
        )


class QidEditView(BaseQidView):
    """View to render edit popup and process updates for an existing QID record."""

    def get(self) -> Response | str:
        """Render edit modal popup."""
        qid_id_raw = request.args.get("id", "")
        try:
            qid_id = int(qid_id_raw)
        except (ValueError, TypeError):
            flash(f"Invalid ID: {qid_id_raw}", "danger")
            return redirect(url_for("adminpanel.edit_done"))

        record: QidRecord | QidOthersRecord | None = self.service.get_by_id(qid_id)
        if not record:
            flash(f"Record not found. id={qid_id}", "danger")
            return redirect(url_for("adminpanel.edit_done"))

        return render_template(
            "admins/qids/edit.html",
            id=qid_id,
            title=record.title,
            qid=record.qid,
            qid_table=self.endpoint,
            post_endpoint=f"adminpanel.{self.endpoint}.edit",
        )

    def post(self) -> ResponseReturnValue:
        """Process update request for a record."""
        qid_id_raw = (request.form.get("id") or "").strip()
        title = (request.form.get("title") or "").strip()
        qid = (request.form.get("qid") or "").strip()

        edit_done_ep = redirect(url_for("adminpanel.edit_done"))

        try:
            qid_id = int(qid_id_raw)
        except ValueError:
            flash(f"Invalid id: {qid_id_raw}", "danger")
            return edit_done_ep

        edit_redirect_to = redirect(url_for(f"adminpanel.{self.endpoint}.edit", id=qid_id))

        if not title:
            flash(f"Title is required. qid=({qid})", "danger")
            return edit_redirect_to

        if not qid:
            flash(f"Qid is required. title=({title})", "danger")
            return edit_redirect_to

        try:
            if not self.is_valid_qid(qid_id, qid, title):
                return edit_redirect_to
        except Exception:
            logger.exception("Failed to save qids row id=%r title=%r qid=%r", qid_id, title, qid)
            flash(f"Failed to check data for title: {title}, Qid: {qid}.", "danger")
            return edit_redirect_to

        try:
            ok = self.service.update_qid(qid_id, title, qid)
        except Exception:
            logger.exception("Failed to save row id=%r title=%r qid=%r", qid_id, title, qid)
            ok = False

        if ok:
            flash(f"Data saved successfully for title: {title}, Qid: {qid}.", "success")
            return edit_done_ep

        flash(f"Failed to save data for title: {title}, Qid: {qid}.", "danger")
        return edit_redirect_to


class QidAddView(BaseQidView):
    """View to render creation popup and insert new QID record."""

    def get(self) -> str:
        """Render add record modal popup."""
        return render_template(
            "admins/qids/edit.html",
            new=1,
            title="",
            qid="",
            qid_table=self.endpoint,
            post_endpoint=f"adminpanel.{self.endpoint}.add",
        )

    def post(self) -> ResponseReturnValue:
        """Process insertion request for new record."""
        title = (request.form.get("title") or "").strip()
        qid = (request.form.get("qid") or "").strip()

        edit_done_ep = redirect(url_for("adminpanel.edit_done"))
        edit_redirect_to = redirect(url_for(f"adminpanel.{self.endpoint}.add"))

        if not title:
            flash(f"Title is required. qid=({qid})", "danger")
            return edit_redirect_to

        if not qid:
            flash(f"Qid is required. title=({title})", "danger")
            return edit_redirect_to

        try:
            if not self.is_valid_qid(False, qid, title):
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


class QidsSharedModelView:
    """Base class for registering shared QID MethodViews on a Blueprint."""

    def __init__(
        self,
        endpoint: str,
        title_label: str,
        service: QidService | QidOthersService,
    ) -> None:
        self.endpoint = endpoint
        self.title_label = title_label
        self.service = service

    def register(self, bp: Blueprint) -> None:
        """Register URL rules for QID management views on the provided blueprint."""
        view_args = (self.endpoint, self.title_label, self.service)

        bp.add_url_rule("/", view_func=QidIndexView.as_view("index", *view_args))
        bp.add_url_rule("/edit", view_func=QidEditView.as_view("edit", *view_args))
        bp.add_url_rule("/add", view_func=QidAddView.as_view("add", *view_args))

        # ------------------------------------------------------------------
        # TODO: Backward Compatibility / Temporary Aliases
        # Legacy POST endpoints 'edit_post' and 'add_post' have been merged
        # into QidEditView and QidAddView POST handlers. Remove these temporary
        # rules once all template forms and url_for calls are updated.
        # ------------------------------------------------------------------
        bp.add_url_rule(
            "/", endpoint="edit_post", view_func=QidEditView.as_view("legacy_edit_post", *view_args), methods=["POST"]
        )
        bp.add_url_rule(
            "/add", endpoint="add_post", view_func=QidAddView.as_view("legacy_add_post", *view_args), methods=["POST"]
        )


__all__ = [
    "QidIndexView",
    "QidEditView",
    "QidAddView",
    "QidsSharedModelView",
]
