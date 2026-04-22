"""
Routes for the 'Fix References' feature.
This blueprint provides a user interface for processing text to fix references
using the `do_changes_to_text_with_settings` service.
"""

import logging
import random

from flask import (
    Blueprint,
    flash,
    render_template,
    request,
)

from ....shared.auth import oauth_required

from ....shared.clients.text_api import get_wikitext

from ....shared.utils.helpers.text_processor import (
    do_changes_to_text_with_settings,
)

bp_fixrefs = Blueprint("fixrefs", __name__, url_prefix="/fixrefs")
logger = logging.getLogger(__name__)


@bp_fixrefs.route("/", methods=["GET"])
def index() -> str:
    return render_template(
        "fixrefs/index.html",
        result=None,
        form={},
    )


@oauth_required
@bp_fixrefs.route("/test", methods=["GET"])
def test() -> str:
    tests_data = [
        {
            "source_title": "Decitabine/cedazuridine",
            "title": "Decitabina/cedazuridina",
            "lang": "es",
            "mdwiki_revid": 1478161,
        },
        {
            "source_title": "Tropicamide",
            "title": "Usuario:Mr. Ibrahem/Tropicamida",
            "lang": "es",
            "mdwiki_revid": 1408734,
        },
        {
            "source_title": "Fatty liver disease",
            "title": "Մասնակից:Mr. Ibrahem/Լյարդի ճարպային հիվանդություն",
            "lang": "hy",
            "mdwiki_revid": 1458412,
        }
    ]
    item = random.choice(tests_data)

    return render_template(
        "fixrefs/index.html",
        **item,
        form={
            "infobox": 1,
        },
    )


@oauth_required
@bp_fixrefs.route("/", methods=["POST"])
def process_new() -> str:

    source_title = request.form.get("source_title", "")
    title = request.form.get("title", "")
    text = request.form.get("text", "")
    lang = request.form.get("lang", "")
    mdwiki_revid_raw = request.form.get("mdwiki_revid", "").strip()

    try:
        mdwiki_revid = int(mdwiki_revid_raw or 0)
    except ValueError:
        flash("Invalid MDWiki revision ID.", "warning")
        mdwiki_revid = 0

    save = request.form.get("save", "").lower() in {"1", "true", "on", "yes"}
    infobox = request.form.get("infobox", "").lower() in {"1", "true", "on", "yes"}
    movedots = request.form.get("movedots", "").lower() in {"1", "true", "on", "yes"}
    # add_en_lang = request.form.get("add_en_lang", "").lower() in {"1", "true", "on", "yes"}
    # add_category = request.form.get("add_category", "").lower() in {"1", "true", "on", "yes"}

    if not text and lang and title:
        text = get_wikitext(title, project=f"{lang}.wikipedia.org") or ""

    try:
        result = do_changes_to_text_with_settings(
            text=text,
            title=title,
            lang=lang,
            source_title=source_title,
            mdwiki_revid=mdwiki_revid,
            move_dots=movedots,
            expend_infobox=infobox,
            # add_en_lang=add_en_lang,
            # add_category=add_category,
        )
    except Exception:
        logger.exception("Error processing text")
        result = "An error occurred while processing the text. Please check the logs for details."

    result = result or ""
    no_changes = result.strip() == text.strip()

    if no_changes:
        flash("No changes were made to the text.", "warning")

    return render_template(
        "fixrefs/index.html",
        no_changes=no_changes,
        source_title=source_title,
        title=title,
        lang=lang,
        mdwiki_revid=mdwiki_revid,
        text=text,
        result=result,
        form={
            "save": save,
            "infobox": infobox,
            "movedots": movedots,
        },
    )


__all__ = ["bp_fixrefs"]
