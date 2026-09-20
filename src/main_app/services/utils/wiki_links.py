"""
URL and HTML link builders ported from the PHP Translation-Dashboard.

Each builder returns a plain string. HTML-returning helpers produce
already-escaped, browser-safe markup; templates render their output with
``|safe`` because the only dynamic inputs are URL components run through
``urllib.parse.quote``.

Reference PHP modules:
  - src/frontend/html.php
      - make_mdwiki_href
      - make_mdwiki_article_url_blank
      - make_mdwiki_cat_url
      - make_wikipedia_url_blank
      - make_wikidata_url_blank
  - src/backend/results/tr_link.php
      - make_tr_link_medwiki
      - make_ContentTranslation_url
  - src/backend/api_or_sql/data_tab.php
      - get_endpoint
"""

from __future__ import annotations

from html import escape
from urllib.parse import quote, urlencode

from flask import url_for

from ...database.services import SettingsService

# Mirrors PHP make_ContentTranslation_url's default. The setting key
# `use_mdwikicx` (read by `_get_endpoint`) flips this to mdwikicx.
_DEFAULT_ENDPOINT = "https://mdwikicx.toolforge.org/w/index.php"
_MDWIKICX_ENDPOINT = "https://mdwikicx.toolforge.org/w/index.php"


def _wiki_path(title: str) -> str:
    """PHP-equivalent ``rawurlencode(str_replace(' ', '_', $title))``."""
    return quote(title.replace(" ", "_"))


def mdwiki_cat_link(category: str, name: str | None = None) -> str:
    """``<a target="_blank">`` for a mdwiki category (PHP make_mdwiki_cat_url)."""
    if not category:
        return category or ""
    clean = category.replace("Category:", "")
    display = escape(name if name else clean)
    encoded = quote(clean.replace(" ", "_"))
    return f"<a target='_blank' href='https://mdwiki.org/wiki/Category:{encoded}'>{display}</a>"


def wikipedia_link(
    target: str,
    lang: str,
    name: str = "",
    deleted: bool = False,
) -> str:
    """``<a target="_blank">`` for a Wikipedia article (PHP make_wikipedia_url_blank)."""
    if not target:
        return target or ""
    display = escape(name if name else target)
    encoded = _wiki_path(target)
    safe_lang = escape(lang or "")
    link = f"<a target='_blank' href='https://{safe_lang}.wikipedia.org/wiki/{encoded}'>{display}</a>"
    if deleted:
        link += ' <span class="text-danger">(DELETED)</span>'
    return link


def wikidata_link(qid: str, name: str = "", default: str = "") -> str:
    """``<a target="_blank">`` for a Wikidata QID (PHP make_wikidata_url_blank)."""
    if not qid:
        return default or ""
    display = escape(name if name else qid)
    encoded = quote(qid.replace(" ", "_"))
    return f"<a class='inline' target='_blank' href='https://wikidata.org/wiki/{encoded}'>{display}</a>"


def tr_link_medwiki(title: str, langcode: str, cat: str, camp: str, tra_type: str, word: int | str = 0) -> str:
    """Relative URL to ``translate_med.php`` (PHP make_tr_link_medwiki).

    The target endpoint is hosted by the PHP Translation-Dashboard. The
    Python port preserves the exact relative path used elsewhere in the
    publish_py templates so the existing dashboard handles the request.
    """
    params = {
        "title": title,
        "langcode": langcode,
        "cat": cat,
        "camp": camp,
        "word": str(word),
        "tra_type": tra_type,
    }
    translate_med_url = url_for("translate_med.index", **params, _external=False)
    return translate_med_url


def content_translation_url(
    title: str,
    code: str,
    campaign: str | None,
    tra_type: str,
    endpoint: str = "",
) -> str:
    """Special:ContentTranslation URL (PHP make_ContentTranslation_url)."""
    # PHP: $title = str_replace('%20', '_', $title);
    # title = title.replace("%20", "_")

    # Callers may pass either raw titles (`Foo Bar`) or pre-encoded titles (`Foo%20Bar`).
    # Normalize both forms before query encoding so the output matches the PHP `_` form.
    title = title.replace("%20", "_").replace(" ", "_")

    if not endpoint:
        endpoint = get_endpoint()

    params = {
        "title": "Special:ContentTranslation",
        "tr_type": tra_type,
        "from": "mdwiki",
        "to": code,
        "campaign": campaign or "",
        "page": title,
    }
    return endpoint + "?" + urlencode(params, quote_via=quote)


def get_endpoint() -> str:
    """ """
    return _MDWIKICX_ENDPOINT


__all__ = [
    "mdwiki_cat_link",
    "wikipedia_link",
    "wikidata_link",
    "tr_link_medwiki",
    "content_translation_url",
    "get_endpoint",
]
