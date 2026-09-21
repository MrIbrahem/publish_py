"""
Admin-only routes for managing campaigns.
"""

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

from ...database.services import CategoryService
from ..decorators import admin_required

logger = logging.getLogger(__name__)


class BaseCampaignsView(MethodView):
    """Base view for the campaign management pages.

    Holds the category service shared by every campaign page. Note that
    only the dashboard requires an administrator; the write endpoints
    declare ``admin_required`` themselves to match the legacy behavior.
    """

    def __init__(self) -> None:
        self.category_service = CategoryService()

    def _update_category(
        self,
        category_id: int,
        category: str,
        campaign: str,
        display: str | None = "",
        category2: str | None = "",
        depth: int | str = 0,
        is_default: int = 0,
    ) -> None:
        """Update an existing category record."""
        try:
            record = self.category_service.update_category(
                category_id=category_id,
                category=category,
                campaign=campaign,
                display=display,
                category2=category2,
                depth=depth,
                is_default=is_default,
            )
        except ValueError as exc:
            logger.exception("Unable to update category")
            flash(str(exc), "warning")
        except Exception:
            logger.exception("Unable to update category.")
            flash("Unable to update category. Please try again.", "danger")
        else:
            flash(f"category for '{record.category}' updated.", "success")

    def _delete_category(self, record_id: int) -> None:
        """Remove a category record entirely."""

        try:
            record = self.category_service.delete(record_id)
            if not record:
                raise ValueError("Category not found")
        except ValueError as exc:
            logger.exception("Unable to delete category")
            flash(str(exc), "warning")
        except Exception:
            logger.exception("Unable to delete category.")
            flash("Unable to delete category. Please try again.", "danger")
        else:
            flash(f"category for '{record_id}' removed.", "success")


class CampaignsDashboardView(BaseCampaignsView):
    """Render the campaigns management dashboard."""

    decorators = [admin_required]

    def get(self) -> str:
        """Render the campaigns management dashboard."""

        campaigns = self.category_service.list_categories()

        return render_template(
            "admins/campaigns.html",
            campaigns=campaigns,
        )


class CampaignsAddRecordView(BaseCampaignsView):
    """Create a new category record."""

    def post(self) -> ResponseReturnValue:
        """Create a new category record."""
        category = request.form.get("category", "").strip()
        campaign = request.form.get("campaign", "").strip()
        if not category:
            flash("Category is required.", "danger")
            return redirect(url_for("adminpanel.campaigns.dashboard"))

        if not campaign:
            flash("Campaign is required.", "danger")
            return redirect(url_for("adminpanel.campaigns.dashboard"))

        try:
            self.category_service.add_category(
                category=category,
                campaign=campaign,
            )
        except ValueError as exc:
            logger.exception("Unable to add category")
            flash(str(exc), "warning")
        except Exception:
            logger.exception("Unable to add category.")
            flash("Unable to add category. Please try again.", "danger")
        else:
            flash(f"category for '{category}' added.", "success")

        return redirect(url_for("adminpanel.campaigns.dashboard"))

class CampaignsUpdateView(BaseCampaignsView):
    """Apply the bulk category edits submitted from the dashboard."""

    def post(self) -> ResponseReturnValue:
        default_cat = request.form.get("default_cat")
        ids = request.form.getlist("rows[][id]")
        campaigns = request.form.getlist("rows[][campaign]")
        categories = request.form.getlist("rows[][category]")
        categories2 = request.form.getlist("rows[][category2]")
        depths = request.form.getlist("rows[][depth]")
        displays = request.form.getlist("rows[][display]")
        deletes = request.form.getlist("rows[][delete]")

        def get_val(lst: list[str], idx: int) -> str:
            return lst[idx].strip() if idx < len(lst) else ""

        for i, id in enumerate(ids):
            is_default = id == default_cat
            record_id = int(id)
            campaign = get_val(campaigns, i)
            category = get_val(categories, i)
            category2 = get_val(categories2, i)
            display = get_val(displays, i)
            depth = get_val(depths, i)
            is_deleted = str(record_id) in deletes

            if is_deleted:
                self._delete_category(record_id)
            elif category:
                self._update_category(
                    category_id=record_id,
                    category=category,
                    campaign=campaign,
                    display=display,
                    category2=category2,
                    depth=depth,
                    is_default=is_default,
                )

        return redirect(url_for("adminpanel.campaigns.dashboard"))


class CampaignsDashboard:
    """Registrar wiring the campaign MethodViews onto a blueprint.

    Endpoint names (``dashboard``, ``add_record``, ``update``) are
    preserved from the legacy function-based routes so existing
    ``url_for('adminpanel.campaigns.add_record')`` calls keep working.
    """

    def register(self, bp: Blueprint) -> None:
        """Register the dashboard, add and update endpoints."""
        bp.add_url_rule("/", view_func=CampaignsDashboardView.as_view("dashboard"), methods=["GET"])
        bp.add_url_rule("/add", view_func=CampaignsAddRecordView.as_view("add_record"), methods=["POST"])
        bp.add_url_rule("/update", view_func=CampaignsUpdateView.as_view("update"), methods=["POST"])


__all__ = [
    "CampaignsDashboard",
]
