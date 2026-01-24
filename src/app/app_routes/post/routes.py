"""
TODO: should be mirror php_src/endpoints/post.php
"""

import logging

from flask import (
    Blueprint,
    render_template,
)

from ...users.current import current_user, oauth_required

bp_post = Blueprint("post", __name__)
logger = logging.getLogger(__name__)


@oauth_required
@bp_post.post("/")
def index(): ...


__all__ = ["bp_post"]
