"""
Routes for the 'Fix References' feature.
This blueprint provides a user interface for processing text to fix references
using the `do_changes_to_text` service.
"""

import logging

from flask import (
    Blueprint,
    flash,
    render_template,
    request,
)
from ....shared.clients.text_api import get_wikitext

from ....shared.utils.helpers.text_processor import (
    do_changes_to_text,
    do_changes_to_text_with_settings,
)

bp_fixrefs = Blueprint("fixrefs", __name__, url_prefix="/fixrefs")
logger = logging.getLogger(__name__)


@bp_fixrefs.route("/", methods=["GET"])
def index() -> str:
    return render_template(
        "fix-refs.html",
        result=None,
        form={},
    )


@bp_fixrefs.route("/", methods=["POST"])
def process_new() -> str:

    source_title = request.form.get("source_title", "")
    title = request.form.get("title", "")
    text = request.form.get("text", "")
    lang = request.form.get("lang", "")
    mdwiki_revid = request.form.get("mdwiki_revid", "")

    save = request.form.get("save", "")
    infobox = request.form.get("infobox", "")
    movedots = request.form.get("movedots", "")

    if not text and lang and title:
        text = get_wikitext(title, project=f"{lang}.wikipedia.org")

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
        "fix-refs.html",
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
