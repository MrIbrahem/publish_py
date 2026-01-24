"""
TODO: should be mirror php_src/endpoints/token.php

should only accept requests from specific domains

function is_allowed()
{
    $domains = ['medwiki.toolforge.org', 'mdwikicx.toolforge.org'];
    $referer = isset($_SERVER['HTTP_REFERER']) ? $_SERVER['HTTP_REFERER'] : '';
    $origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : '';

    $is_allowed = false;
    foreach ($domains as $domain) {
        if (strpos($referer, $domain) !== false || strpos($origin, $domain) !== false) {
            $is_allowed = $domain;
            break;
        }
    }
    return $is_allowed;
}

"""

import logging

from flask import (
    Blueprint,
    render_template,
)

from ..users.current import current_user, oauth_required

bp_cxtoken = Blueprint("token", __name__)
logger = logging.getLogger(__name__)


@oauth_required
@bp_cxtoken.get("/")
def index(): ...


__all__ = ["bp_cxtoken"]
