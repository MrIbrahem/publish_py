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

from ...database.services import FullTranslatorService
from ..decorators import admin_required

logger = logging.getLogger(__name__)


class FullTranslators:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self.service = FullTranslatorService()
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["GET"])(admin_required(self.dashboard))
        self.bp.post("/add")(admin_required(self.add))
        self.bp.post("/<int:translator_id>/delete")(admin_required(self.delete))
        self.bp.post("/<int:record_id>/activate")(admin_required(self.activate))
        self.bp.post("/<int:record_id>/deactivate")(admin_required(self.deactivate))

    def dashboard(self):
        """Render the full translator management dashboard."""
        translators = self.service.list_full_translators()
        total = len(translators)
        is_active = sum(1 for tr in translators if tr.is_active)

        return render_template(
            "admins/full_translators.html",
            translators=translators,
            total_translators=total,
            active_translators=is_active,
            inactive_translators=total - is_active,
        )

    def add(self) -> ResponseReturnValue:
        """Create a new full translator from the submitted username."""

        username = request.form.get("username", "").strip()
        if not username:
            flash("Username is required to add a full translator.", "danger")
            return redirect(url_for("adminpanel.full_translators.dashboard"))

        try:

            record = self.service.add_full_translator(username)
        except ValueError as exc:
            logger.exception("Unable to add full translator")
            flash(str(exc), "warning")
        except Exception:
            logger.exception("Unable to add full translator.")
            flash("Unable to add full translator. Please try again.", "danger")
        else:
            flash(f"Full translator '{record.user}' added.", "success")

        return redirect(url_for("adminpanel.full_translators.dashboard"))

    def delete(self, translator_id: int) -> ResponseReturnValue:
        """Remove a full translator entirely."""

        try:
            record = self.service.delete(translator_id)
            if not record:
                raise ValueError(f"Unable to delete full translator with ID {translator_id}")
        except ValueError as exc:
            logger.exception("Unable to delete full translator")
            flash(str(exc), "warning")
        except Exception:
            logger.exception("Unable to delete full translator.")
            flash("Unable to delete full translator. Please try again.", "danger")
        else:
            flash(f"Full translator '{translator_id}' removed.", "success")

        return redirect(url_for("adminpanel.full_translators.dashboard"))

    def activate(self, record_id: int) -> ResponseReturnValue:
        return self._set_record_active_status(record_id, True)

    def deactivate(self, record_id: int) -> ResponseReturnValue:
        return self._set_record_active_status(record_id, False)

    def _set_record_active_status(self, record_id: int, is_active: bool) -> ResponseReturnValue:
        """Shared helper to update record active status."""
        action = "activate" if is_active else "deactivate"
        try:

            record = self.service.update_full_translator(record_id, is_active=is_active)
        except LookupError as exc:
            logger.exception(f"Unable to {action} coordinator.")
            flash(str(exc), "warning")
        except Exception:  # pragma: no cover - defensive guard
            logger.exception(f"Unable to {action} record.")
            flash(f"Unable to {action} record. Please try again.", "danger")
        else:
            state = "activated" if record.is_active else "deactivated"
            flash(f"Record '{record.user}' {state}.", "success")

        return redirect(url_for("adminpanel.full_translators.dashboard"))


__all__ = [
    "FullTranslators",
]
