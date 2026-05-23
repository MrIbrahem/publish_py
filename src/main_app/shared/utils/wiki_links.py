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
from typing import Optional
from urllib.parse import quote, urlencode

# Mirrors PHP make_ContentTranslation_url's default. The setting key
# `use_mdwikicx` (read by `_get_endpoint`) flips this to mdwikicx.
_DEFAULT_ENDPOINT = "https://medwiki.toolforge.org/w/index.php"
_MDWIKICX_ENDPOINT = "https://mdwikicx.toolforge.org/w/index.php"


def _php_rawurlencode(value: str) -> str:
    """PHP ``rawurlencode`` — RFC 3986 percent-encoding."""
    return quote(value, safe="")


def _wiki_path(title: str) -> str:
    """PHP-equivalent ``rawurlencode(str_replace(' ', '_', $title))``."""
    return _php_rawurlencode(title.replace(" ", "_"))


def mdwiki_url(title: str) -> str:
    """Plain URL to a mdwiki article (PHP make_mdwiki_href)."""
    if not title:
        return title or ""
    return f"https://mdwiki.org/wiki/{_wiki_path(title)}"


def mdwiki_article_link(title: str, name: Optional[str] = None) -> str:
    """``<a target="_blank">`` for a mdwiki article (PHP make_mdwiki_article_url_blank)."""
    if not title:
        return title or ""
    display = escape(name if name else title)
    encoded = _wiki_path(title)
    return f"<a target='_blank' href='https://mdwiki.org/wiki/{encoded}'>{display}</a>"


def mdwiki_cat_link(category: str, name: Optional[str] = None) -> str:
    """``<a target="_blank">`` for a mdwiki category (PHP make_mdwiki_cat_url)."""
    if not category:
        return category or ""
    clean = category.replace("Category:", "")
    display = escape(name if name else clean)
    encoded = _php_rawurlencode(clean.replace(" ", "_"))
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
    encoded = _php_rawurlencode(qid.replace(" ", "_"))
    return f"<a class='inline' target='_blank' href='https://wikidata.org/wiki/{encoded}'>{display}</a>"


def tr_link_medwiki(title: str, cod: str, cat: str, camp: str, tra_type: str, word: int | str) -> str:
    """Relative URL to ``translate_med/index.php`` (PHP make_tr_link_medwiki).

    The target endpoint is hosted by the PHP Translation-Dashboard. The
    Python port preserves the exact relative path used elsewhere in the
    publish_py templates so the existing dashboard handles the request.
    """
    params = {
        "title": _php_rawurlencode(title),  # PHP encodes the title twice (rawurlEncode + http_build_query RFC 3986)
        "code": cod,
        "cat": _php_rawurlencode(cat),
        "camp": _php_rawurlencode(camp),
        "word": str(word),
        "type": tra_type,
    }
    # Match PHP http_build_query(..., PHP_QUERY_RFC3986) — encodes via rawurlencode, joins with `&`.
    return "translate_med/index.php?" + urlencode(params, quote_via=quote)


def content_translation_url(
    title: str,
    cod: str,
    cat: str,  # noqa: ARG001 — kept for parity with the PHP signature
    campaign: str,
    tra_type: str,
    endpoint: str,
) -> str:
    """Special:ContentTranslation URL (PHP make_ContentTranslation_url)."""
    # PHP: $title = str_replace('%20', '_', $title);
    # title = title.replace("%20", "_")

    # Callers may pass either raw titles (`Foo Bar`) or pre-encoded titles (`Foo%20Bar`).
    # Normalize both forms before query encoding so the output matches the PHP `_` form.
    title = title.replace("%20", "_").replace(" ", "_")

    params = {
        "title": "Special:ContentTranslation",
        "tr_type": tra_type,
        "from": "mdwiki",
        "to": cod,
        "campaign": campaign,
        "page": title,
    }
    return endpoint + "?" + urlencode(params, quote_via=quote)


def get_endpoint() -> str:
    """Return the ContentTranslation endpoint based on the ``use_mdwikicx`` setting.

    The setting lookup is wrapped in a try/except so that a missing key,
    a missing table, or a connection issue all degrade gracefully to the
    default endpoint — matching the PHP behavior where ``get_endpoint``
    returns the default when the setting is absent or falsy.
    """
    # Imported lazily to avoid pulling Flask-SQLAlchemy at import time.
    try:
        from ...db.services.config.setting_service import get_setting_by_key

        record = get_setting_by_key("use_mdwikicx")
    except Exception:
        return _DEFAULT_ENDPOINT

    if record is None:
        return _DEFAULT_ENDPOINT

    raw = (record.value or "").strip().lower()
    truthy = raw == "1"
    return _MDWIKICX_ENDPOINT if truthy else _DEFAULT_ENDPOINT


__all__ = [
    "mdwiki_url",
    "mdwiki_article_link",
    "mdwiki_cat_link",
    "wikipedia_link",
    "wikidata_link",
    "tr_link_medwiki",
    "content_translation_url",
    "get_endpoint",
]
