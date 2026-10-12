"""
Services for external API integration.

Used in both admin and public blueprints.
"""

from __future__ import annotations

from .mediawiki_api import MediaWikiApiClient, get_title_info, publish_do_edit
from .oauth_client import OAuthClient, get_csrf_token, get_cxtoken, get_oauth_client, post_params
from .text_api import TextApiClient, get_wikitext
from .wikidata_client import WikidataClient, get_qid_for_mdtitle, link_to_wikidata

__all__ = [
    "MediaWikiApiClient",
    "OAuthClient",
    "TextApiClient",
    "WikidataClient",
    "get_oauth_client",
    "get_csrf_token",
    "post_params",
    "get_cxtoken",
    "publish_do_edit",
    "get_qid_for_mdtitle",
    "get_title_info",
    "link_to_wikidata",
    "get_wikitext",
]
