"""Admin routes for the ``qids_others`` table.

Same shape as ``qids.py`` but targets ``qids_others``.
"""

from __future__ import annotations

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

from ...db.services.wikidata import qid_others_service

logger = logging.getLogger(__name__)


qids_others_bp = Blueprint("qids_others", __name__, url_prefix="/qids_others")

VALID_DIS = {"all", "empty", "duplicate"}


@qids_others_bp.route("/", methods=["GET"])
def qids_others_index() -> str:
    """List qids_others rows with optional filter (all / empty / duplicate)."""
    dis = request.args.get("dis", "all")
    if dis not in VALID_DIS:
        dis = "all"

    try:
        rows = qid_others_service.list_qids_others(dis=dis)
    except Exception:
        logger.exception("Failed to list qids_others dis=%r", dis)
        rows = []

    return render_template(
        "admins/qids/index.html",
        rows=rows,
        dis=dis,
        qid_table="qids_others",
        title_label="Qids Others",
        index_endpoint="admin.qids_others.qids_others_index",
        edit_endpoint="admin.qids_others.qids_others_edit",
        post_endpoint="admin.qids_others.qids_others_post",
    )


@qids_others_bp.route("/edit", methods=["GET"])
def qids_others_edit() -> str:
    """Render the add/edit popup for a single qids_others row."""
    return render_template(
        "admins/qids/edit.html",
        id=request.args.get("id", ""),
        title=request.args.get("title", ""),
        qid=request.args.get("qid", ""),
        qid_table="qids_others",
        post_endpoint="admin.qids_others.qids_others_post",
    )


@qids_others_bp.route("/", methods=["POST"])
def qids_others_post() -> ResponseReturnValue:
    """Insert or update a qids_others row, with same validation as qids."""
    qid_id_raw = (request.form.get("id") or "").strip()
    title = (request.form.get("title") or "").strip()
    qid = (request.form.get("qid") or "").strip()

    redirect_to = redirect(url_for("admin.qids_others.qids_others_index"))

    if not title:
        flash(f"Title is required. qid=({qid})", "danger")
        return redirect_to
    if not qid:
        flash(f"Qid is required. title=({title})", "danger")
        return redirect_to

    qid_id: int | None = None
    if qid_id_raw:
        try:
            qid_id = int(qid_id_raw)
        except ValueError:
            flash(f"Invalid id: {qid_id_raw}", "danger")
            return redirect_to

    try:
        existing_by_qid = qid_others_service.get_by_qid(qid)
        if existing_by_qid:
            if qid_id and existing_by_qid.id != qid_id:
                flash(
                    f"Qid:({qid}) already used in database with id:({existing_by_qid.id}).",
                    "danger",
                )
                return redirect_to
            if not qid_id and existing_by_qid.title and existing_by_qid.title != title:
                flash(
                    f"Qid:({qid}) already used in database with title:({existing_by_qid.title}).",
                    "danger",
                )
                return redirect_to

        existing_by_title = qid_others_service.get_by_title(title)
        if existing_by_title:
            if qid_id and existing_by_title.id != qid_id:
                flash(
                    f"Title:({title}) already used in database with qid:"
                    f"({existing_by_title.qid}), new qid:({qid})",
                    "danger",
                )
                return redirect_to
            if not qid_id and existing_by_title.qid and existing_by_title.qid != qid:
                flash(
                    f"Title:({title}) already used in database with qid:"
                    f"({existing_by_title.qid}), new qid:({qid})",
                    "danger",
                )
                return redirect_to

        if qid_id:
            ok = qid_others_service.update(qid_id, title, qid)
        else:
            ok = qid_others_service.insert(title, qid)
    except Exception:
        logger.exception(
            "Failed to save qids_others row id=%r title=%r qid=%r", qid_id, title, qid
        )
        ok = False

    if ok:
        flash(f"Data saved successfully for title: {title}, Qid: {qid}.", "success")
    else:
        flash(f"Failed to save data for title: {title}, Qid: {qid}.", "danger")

    return redirect_to
