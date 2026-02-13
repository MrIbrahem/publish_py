"""
Routes for the 'Fix References' feature.
This blueprint provides a user interface for processing text to fix references
using the `do_changes_to_text` service.
"""

import logging

from flask import (
    Blueprint,
    render_template,
    request,
)

from ...users.current import current_user
from ...services.text_processor import do_changes_to_text

bp_fixrefs = Blueprint("fixrefs", __name__)
logger = logging.getLogger(__name__)


@bp_fixrefs.route("/", methods=["GET"])
def index() -> str:
    current_user_obj = current_user()
    return render_template(
        "fix-refs.html",
        result=None,
        current_user=current_user_obj,
    )


@bp_fixrefs.route("/", methods=["POST"])
def process() -> str:
    current_user_obj = current_user()

    source_title = request.form.get("sourceTitle", "")
    title = request.form.get("title", "")
    text = request.form.get("text", "")
    lang = request.form.get("lang", "")
    mdwiki_revid = request.form.get("mdwikiRevid", "")

    try:
        result = do_changes_to_text(
            sourcetitle=source_title,
            title=title,
            text=text,
            lang=lang,
            mdwiki_revid=mdwiki_revid,
        )
    except Exception:
        logger.exception("Error processing text")
        result = "An error occurred while processing the text. Please check the logs for details."

    return render_template(
        "fix-refs.html",
        current_user=current_user_obj,
        sourceTitle=source_title,
        title=title,
        lang=lang,
        mdwiki_revid=mdwiki_revid,
        text=text,
        result=result,
    )


__all__ = ["bp_fixrefs"]
