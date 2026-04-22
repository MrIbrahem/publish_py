"""
Services for external API integration.

Used in both admin and public blueprints.
"""

from .mediawiki_api import get_title_info, publish_do_edit
from .oauth_client import get_csrf_token, get_cxtoken, get_oauth_client, post_params
from .revids_client import get_revid, get_revid_db
from .wikidata_client import get_qid_for_mdtitle, link_to_wikidata

__all__ = [
    "get_oauth_client",
    "get_csrf_token",
    "post_params",
    "get_cxtoken",
    "publish_do_edit",
    "get_revid",
    "get_revid_db",
    "get_qid_for_mdtitle",
    "get_title_info",
    "link_to_wikidata",
]
