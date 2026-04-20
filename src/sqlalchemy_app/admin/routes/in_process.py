"""Admin-only routes for viewing detailed in-process translations."""

from __future__ import annotations

import logging

from flask import Blueprint, render_template

from ..decorators import admin_required
from ...public.services.in_process_service import list_in_process
from ...public.services.lang_service import get_lang_by_code

logger = logging.getLogger(__name__)


def _in_process_dashboard():
    """Render the detailed in-process dashboard."""

    in_process_records = list_in_process()

    # Enrich records with language names
    enriched_records = []
    for record in in_process_records:
        lang_record = get_lang_by_code(record.lang)
        lang_name = lang_record.name if lang_record else record.lang
        enriched_records.append({
            "id": record.id,
            "user": record.user,
            "lang_code": record.lang,
            "lang_name": lang_name,
            "title": record.title,
            "campaign": record.cat,
            "draft_date": record.add_date,
        })

    return render_template(
        "admins/in_process.html",
        records=enriched_records,
        total_records=len(enriched_records),
    )


class InProcess:
    def __init__(self, bp_admin: Blueprint):
        @bp_admin.get("/process")
        @admin_required
        def in_process_dashboard():
            return _in_process_dashboard()
