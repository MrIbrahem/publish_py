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

from ...db.services import CategoryService
from ..decorators import admin_required

logger = logging.getLogger(__name__)


class CampaignsDashboard:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self.category_service = CategoryService()
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["GET"])(admin_required(self.dashboard))
        self.bp.post("/add")(admin_required(self.add_record))
        self.bp.post("/update")(admin_required(self.update))

    def dashboard(self):
        """Render the campaigns management dashboard."""

        campaigns = self.category_service.list_categories()

        return render_template(
            "admins/campaigns.html",
            campaigns=campaigns,
        )

    def add_record(self) -> ResponseReturnValue:
        """Create a new category record."""
        category = request.form.get("category", "").strip()
        campaign = request.form.get("campaign", "").strip()
        if not category:
            flash("Category is required.", "danger")
            return redirect(url_for("admin.campaigns.dashboard"))

        if not campaign:
            flash("Campaign is required.", "danger")
            return redirect(url_for("admin.campaigns.dashboard"))

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

        return redirect(url_for("admin.campaigns.dashboard"))

    def update(self) -> ResponseReturnValue:
        default_cat = request.form.get("default_cat")
        ids = request.form.getlist("rows[][id]")
        campaigns = request.form.getlist("rows[][campaign]")
        categories = request.form.getlist("rows[][category]")
        categories2 = request.form.getlist("rows[][category2]")
        depths = request.form.getlist("rows[][depth]")
        displays = request.form.getlist("rows[][display]")
        deletes = request.form.getlist("rows[][delete]")

        for i, id in enumerate(ids):
            is_default = id == default_cat
            record_id = int(id)
            campaign = campaigns[i] if i < len(campaigns) else ""
            category = categories[i] if i < len(categories) else ""
            category2 = categories2[i] if i < len(categories2) else ""
            display = displays[i] if i < len(displays) else ""
            depth = depths[i] if i < len(depths) else 0
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

        return redirect(url_for("admin.campaigns.dashboard"))


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


__all__ = [
    "CampaignsDashboard",
]
