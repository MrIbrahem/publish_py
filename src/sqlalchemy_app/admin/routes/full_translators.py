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

from ..decorators import admin_required
from ...shared.services.full_translator_service import (
    add_full_translator,
    delete_full_translator,
    list_full_translators,
    update_full_translator,
)

logger = logging.getLogger(__name__)


def _full_translators_dashboard():
    """Render the full translator management dashboard."""

    translators = list_full_translators()
    total = len(translators)
    is_active = sum(1 for tr in translators if tr.is_active)

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
        return redirect(url_for("admin.full_translators.dashboard"))

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

    return redirect(url_for("admin.full_translators.dashboard"))


def _set_record_active_status(record_id: int, is_active: bool) -> ResponseReturnValue:
    """Shared helper to update record active status."""
    action = "activate" if is_active else "deactivate"
    past_tense = "activated" if is_active else "deactivated"
    try:
        record = update_full_translator(record_id, is_active)
    except LookupError as exc:
        logger.exception(f"Unable to {action} coordinator.")
        flash(str(exc), "warning")
    except Exception:  # pragma: no cover - defensive guard
        logger.exception(f"Unable to {action} record.")
        flash(f"Unable to {action} record. Please try again.", "danger")
    else:
        flash(f"Record '{record.username}' {past_tense}.", "success")

    return redirect(url_for("admin.full_translators.dashboard"))


def _activate_record(record_id: int) -> ResponseReturnValue:
    """Activate a record."""
    return _set_record_active_status(record_id, True)


def _deactivate_record(record_id: int) -> ResponseReturnValue:
    """Deactivate a record."""
    return _set_record_active_status(record_id, False)


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

    return redirect(url_for("admin.full_translators.dashboard"))


class FullTranslators:
    def __init__(self):
        self.bp = Blueprint("full_translators", __name__, url_prefix="/full_translators")
        self._setup_routes()

    def _setup_routes(self):

        @self.bp.get("/")
        @admin_required
        def dashboard():
            # Call the internal function _full_translators_dashboard to return the full dashboard
            return _full_translators_dashboard()

        @self.bp.post("/add")
        @admin_required
        def add() -> ResponseReturnValue:
            return _add_full_translator()

        @self.bp.post("/<int:translator_id>/delete")
        @admin_required
        def delete(translator_id: int) -> ResponseReturnValue:
            return _delete_full_translator(translator_id)

        @self.bp.post("/<int:record_id>/activate")
        @admin_required
        def activate(record_id: int) -> ResponseReturnValue:
            return _activate_record(record_id)

        @self.bp.post("/<int:record_id>/deactivate")
        @admin_required
        def deactivate(record_id: int) -> ResponseReturnValue:
            return _deactivate_record(record_id)


fulltranslators_module = FullTranslators()
