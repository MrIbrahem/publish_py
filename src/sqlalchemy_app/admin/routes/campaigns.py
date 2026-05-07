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

from ...shared.services.category_service import (
    add_category,
    delete_category,
    get_camp_to_cats,
    get_campaign_category,
    list_categories,
    update_category,
)
from ..decorators import admin_required

logger = logging.getLogger(__name__)


def _campaigns_dashboard():
    """Render the campaigns management dashboard."""

    campaigns = list_categories()

    return render_template(
        "admins/campaigns.html",
        campaigns=campaigns,
    )


def _add_campaign_and_category() -> ResponseReturnValue:
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
        add_category(
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


def _update_category(
    category_id: int,
    category: str,
    campaign: str,
    display: str | None = "",
    category2: str | None = "",
    depth: int = 0,
    is_default: int = 0,
) -> None:
    """Update an existing category record."""

    try:
        record = update_category(
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


def _delete_category(record_id: int) -> None:
    """Remove a category record entirely."""

    try:
        record = delete_category(record_id)
    except ValueError as exc:
        logger.exception("Unable to delete category")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to delete category.")
        flash("Unable to delete category. Please try again.", "danger")
    else:
        flash(f"category for '{record.category}' removed.", "success")


class CampaignsDashboard:
    def __init__(self):
        self.bp = Blueprint("campaigns", __name__, url_prefix="/campaigns")
        self._setup_routes()

    def _setup_routes(self):
        @self.bp.get("/")
        @admin_required
        def dashboard():
            return _campaigns_dashboard()

        @self.bp.post("/add")
        @admin_required
        def add_record() -> ResponseReturnValue:
            return _add_campaign_and_category()

        @self.bp.post("/update")
        @admin_required
        def update() -> ResponseReturnValue:
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
                    _delete_category(record_id)
                elif category:
                    _update_category(
                        category_id=record_id,
                        category=category,
                        campaign=campaign,
                        display=display,
                        category2=category2,
                        depth=depth,
                        is_default=is_default,
                    )

            return redirect(url_for("admin.campaigns.dashboard"))


campaigns_module = CampaignsDashboard()
