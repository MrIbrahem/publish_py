"""

"""

import logging

from flask import (
    Blueprint,
    render_template,
)

from ...users.current import current_user

bp_fixrefs = Blueprint("fixrefs", __name__)
logger = logging.getLogger(__name__)


@bp_fixrefs.get("/")
def index():
    current_user_obj = current_user()
    return render_template(
        "fix-refs.html",
        current_user=current_user_obj,
    )


__all__ = ["bp_fixrefs"]
