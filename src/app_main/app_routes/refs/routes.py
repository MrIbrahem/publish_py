"""

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
def index():
    current_user_obj = current_user()
    return render_template(
        "fix-refs.html",
        current_user=current_user_obj,
    )


@bp_fixrefs.route("/", methods=["POST"])
def process():
    current_user_obj = current_user()
    result = ""
    try:
        result = do_changes_to_text(
            sourcetitle=request.form.get("sourceTitle", ""),
            title=request.form.get("title", ""),
            text=request.form.get("text", ""),
            lang=request.form.get("lang", ""),
            mdwiki_revid=request.form.get("mdwikiRevid", ""),
        )
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        result = f"Error processing text: {e}"

    return render_template(
        "fix-refs.html",
        current_user=current_user_obj,
        sourceTitle=request.form.get("sourceTitle", ""),
        title=request.form.get("title", ""),
        lang=request.form.get("lang", ""),
        mdwiki_revid=request.form.get("mdwikiRevid", ""),
        text=request.form.get("text", ""),
        result=result,
    )


__all__ = ["bp_fixrefs"]
