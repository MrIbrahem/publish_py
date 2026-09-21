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
from flask.views import MethodView

from ...database.services import FullTranslatorService
from ..decorators import admin_required

logger = logging.getLogger(__name__)


class BaseFullTranslatorsView(MethodView):
    """Base view for the full-translator management pages.

    Holds the service shared by every full-translator page and exposes
    the activate/deactivate helper used by the toggle endpoints. All
    full-translator pages require an administrator.
    """

    decorators = [admin_required]

    def __init__(self) -> None:
        self.service = FullTranslatorService()

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


class FullTranslatorsDashboardView(BaseFullTranslatorsView):
    """Render the full translator management dashboard."""

    def get(self) -> str:
        """Render the translators table with active/inactive counts."""
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


class FullTranslatorsAddView(BaseFullTranslatorsView):
    """Create a new full translator from the submitted username."""

    def post(self) -> ResponseReturnValue:
        """Validate the username and add the full translator."""

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


class FullTranslatorsDeleteView(BaseFullTranslatorsView):
    """Remove a full translator entirely."""

    def post(self, translator_id: int) -> ResponseReturnValue:
        """Delete the translator identified by ``translator_id``."""

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


class FullTranslatorsActivateView(BaseFullTranslatorsView):
    """Activate a full translator record."""

    def post(self, record_id: int) -> ResponseReturnValue:
        """Mark the record identified by ``record_id`` as active."""
        return self._set_record_active_status(record_id, True)


class FullTranslatorsDeactivateView(BaseFullTranslatorsView):
    """Deactivate a full translator record."""

    def post(self, record_id: int) -> ResponseReturnValue:
        """Mark the record identified by ``record_id`` as inactive."""
        return self._set_record_active_status(record_id, False)


class FullTranslators:
    """Registrar wiring the full-translator MethodViews onto a blueprint.

    Endpoint names (``dashboard``, ``add``, ``delete``, ``activate``,
    ``deactivate``) are preserved from the legacy function-based routes
    so existing ``url_for('adminpanel.full_translators.add')`` calls keep
    working.
    """

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register the dashboard and the translator write endpoints."""
        bp.add_url_rule("/", view_func=FullTranslatorsDashboardView.as_view("dashboard"), methods=["GET"])
        bp.add_url_rule("/add", view_func=FullTranslatorsAddView.as_view("add"), methods=["POST"])
        bp.add_url_rule(
            "/<int:translator_id>/delete", view_func=FullTranslatorsDeleteView.as_view("delete"), methods=["POST"]
        )
        bp.add_url_rule(
            "/<int:record_id>/activate", view_func=FullTranslatorsActivateView.as_view("activate"), methods=["POST"]
        )
        bp.add_url_rule(
            "/<int:record_id>/deactivate",
            view_func=FullTranslatorsDeactivateView.as_view("deactivate"),
            methods=["POST"],
        )


__all__ = [
    "FullTranslators",
]
