"""Admin-only routes for managing full translators."""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.typing import ResponseReturnValue

from ..sqlalchemy_db.services.full_translator_service import (
    add_full_translator,
    delete_full_translator,
    list_full_translators,
    update_full_translator,
)
from .decorators import admin_required

logger = logging.getLogger(__name__)


def _full_translators_dashboard():
    """Render the full translator management dashboard."""

    translators = list_full_translators()
    total = len(translators)
    is_active = sum(1 for tr in translators if tr.active)

    return render_template(
        "admins/full_translators.html",
        translators=translators,
        total_translators=total,
        active_translators=is_active,
        inactive_translators=total - is_active,
    )


def _add_full_translator() -> ResponseReturnValue:
    """Create a new full translator from the submitted username."""

    username = request.form.get("username", "").strip()
    if not username:
        flash("Username is required to add a full translator.", "danger")
        return redirect(url_for("admin.full_translators_dashboard"))

    try:
        record = add_full_translator(username)
    except ValueError as exc:
        logger.warning(f"Unable to add full translator: {exc}")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to add full translator.")
        flash("Unable to add full translator. Please try again.", "danger")
    else:
        flash(f"Full translator '{record.user}' added.", "success")

    return redirect(url_for("admin.full_translators_dashboard"))


def _update_full_translator_active(translator_id: int) -> ResponseReturnValue:
    """Toggle the active flag for a full translator."""

    active = 1 if request.form.get("active") == "1" else 0
    try:
        record = update_full_translator(translator_id, active=active)
    except ValueError as exc:
        logger.warning(f"Unable to update full translator: {exc}")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to update full translator.")
        flash("Unable to update full translator status. Please try again.", "danger")
    else:
        state = "activated" if record.active else "deactivated"
        flash(f"Full translator '{record.user}' {state}.", "success")

    return redirect(url_for("admin.full_translators_dashboard"))


def _delete_full_translator(translator_id: int) -> ResponseReturnValue:
    """Remove a full translator entirely."""

    try:
        record = delete_full_translator(translator_id)
    except ValueError as exc:
        logger.warning(f"Unable to delete full translator: {exc}")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to delete full translator.")
        flash("Unable to delete full translator. Please try again.", "danger")
    else:
        flash(f"Full translator '{record.user}' removed.", "success")

    return redirect(url_for("admin.full_translators_dashboard"))


class FullTranslators:
    def __init__(self, bp_admin: Blueprint):
        @bp_admin.get("/full_translators")
        @admin_required
        def full_translators_dashboard():
            return _full_translators_dashboard()

        @bp_admin.post("/full_translators/add")
        @admin_required
        def add_full_translator() -> ResponseReturnValue:
            return _add_full_translator()

        @bp_admin.post("/full_translators/<int:translator_id>/active")
        @admin_required
        def update_full_translator_active(translator_id: int) -> ResponseReturnValue:
            return _update_full_translator_active(translator_id)

        @bp_admin.post("/full_translators/<int:translator_id>/delete")
        @admin_required
        def delete_full_translator(translator_id: int) -> ResponseReturnValue:
            return _delete_full_translator(translator_id)
