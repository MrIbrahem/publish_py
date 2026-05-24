"""
Admin routes for the ``qids_others`` table.

Same shape as ``qids.py`` but targets ``qids_others``.
"""

from __future__ import annotations

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

from ...db.services.wikidata import qid_others_service as _service

logger = logging.getLogger(__name__)


qids_others_bp = Blueprint("qids_others", __name__, url_prefix="/qids_others")

ENDPOINT_NAME = "qids_others"

VALID_DIS = {"all", "empty", "duplicate"}


def is_valid(qid_id: int | bool, qid: str, title: str) -> bool:
    existing_by_qid = _service.get_by_qid(qid)
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
    existing_by_title = _service.get_by_title(title)
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


@qids_others_bp.route("/", methods=["GET"])
def index() -> str:
    """List of rows with optional filter (all / empty / duplicate)."""
    dis = request.args.get("dis", "all")
    if dis not in VALID_DIS:
        dis = "all"

    try:
        rows = _service.list_records(dis=dis)
    except Exception:
        logger.exception("Failed to list qids rows dis=%r", dis)
        rows = []

    return render_template(
        "admins/qids/index.html",
        rows=rows,
        dis=dis,
        qid_table=ENDPOINT_NAME,
        title_label="Qids Others",
        index_endpoint=f"admin.{ENDPOINT_NAME}.index",
        edit_endpoint=f"admin.{ENDPOINT_NAME}.edit",
        post_endpoint=f"admin.{ENDPOINT_NAME}.edit_post",

        add_endpoint=f"admin.{ENDPOINT_NAME}.add",
    )


@qids_others_bp.route("/edit", methods=["GET"])
def edit() -> str:
    """Render the add/edit popup for a single row."""
    return render_template(
        "admins/qids/edit.html",
        id=request.args.get("id", ""),
        title=request.args.get("title", ""),
        qid=request.args.get("qid", ""),
        qid_table=ENDPOINT_NAME,
        post_endpoint=f"admin.{ENDPOINT_NAME}.edit_post",
    )


@qids_others_bp.route("/add", methods=["GET"])
def add() -> str:
    """Render the add popup for a single qids row."""
    return render_template(
        "admins/qids/edit.html",
        new=1,
        title="",
        qid="",
        qid_table=ENDPOINT_NAME,
        post_endpoint=f"admin.{ENDPOINT_NAME}.add_post",
    )


@qids_others_bp.route("/", methods=["POST"])
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

    edit_redirect_to = redirect(url_for(f"admin.{ENDPOINT_NAME}.edit", id=qid_id))

    if not title:
        flash(f"Title is required. qid=({qid})", "danger")
        return edit_redirect_to

    if not qid:
        flash(f"Qid is required. title=({title})", "danger")
        return edit_redirect_to

    try:
        if not is_valid(qid_id, qid, title):
            return edit_redirect_to

    except Exception:
        logger.exception("Failed to save qids row id=%r title=%r qid=%r", qid_id, title, qid)
        flash(f"Failed to check data for title: {title}, Qid: {qid}.", "danger")
        return edit_redirect_to

    try:
        ok = _service.update(qid_id, title, qid)
    except Exception:
        logger.exception("Failed to save row id=%r title=%r qid=%r", qid_id, title, qid)
        ok = False

    if ok:
        flash(f"Data saved successfully for title: {title}, Qid: {qid}.", "success")
        return edit_done_ep

    flash(f"Failed to save data for title: {title}, Qid: {qid}.", "danger")

    return edit_redirect_to


@qids_others_bp.route("/add", methods=["POST"])
def add_post() -> ResponseReturnValue:
    """Insert a qid row"""
    title = (request.form.get("title") or "").strip()
    qid = (request.form.get("qid") or "").strip()

    edit_done_ep = redirect(url_for("admin.edit_done"))

    edit_redirect_to = redirect(url_for(f"admin.{ENDPOINT_NAME}.add"))

    if not title:
        flash(f"Title is required. qid=({qid})", "danger")
        return edit_redirect_to

    if not qid:
        flash(f"Qid is required. title=({title})", "danger")
        return edit_redirect_to

    try:
        if not is_valid(False, qid, title):
            return edit_redirect_to

    except Exception:
        logger.exception("Failed to save qids row title=%r qid=%r", title, qid)
        flash(f"Failed to check data for title: {title}, Qid: {qid}.", "danger")
        return edit_redirect_to

    try:
        ok = _service.insert(title, qid)
    except Exception:
        logger.exception("Failed to save row title=%r qid=%r", title, qid)
        ok = False

    if ok:
        flash(f"Data saved successfully for title: {title}, Qid: {qid}.", "success")
        return edit_done_ep

    flash(f"Failed to save data for title: {title}, Qid: {qid}.", "danger")

    return edit_redirect_to
