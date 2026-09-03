"""
Template removal utilities.

Port of ``src/Domain/Fixes/Templates/DeleteTemplatesFixture.php``.
"""

from __future__ import annotations

import re

import wikitextparser as wtp

from ...parser import template_helpers as th

try:  # DeadIndexError isn't part of wikitextparser's public API.
    from wikitextparser._wikitext import DeadIndexError
except ImportError:  # pragma: no cover - defensive, in case the private path moves
    DeadIndexError = Exception  # type: ignore[assignment,misc]

#: Template name patterns (lowercase) that should always be removed.
TEMPLATE_DELETE_PATTERNS = (
    # any template startswith pp-
    re.compile(r"^pp(-.*)?$"),
    re.compile(r"^articles (for|with|needing|containing).*$"),
    re.compile(r"^engvar[ab]$"),
    re.compile(r"^use[\sa-z]+(english|spelling|referencing)$"),
    re.compile(r"^use [dmy]+ dates$"),
    re.compile(r"^wikipedia articles (for|with|needing|containing).*$"),
    re.compile(r"^(.*-)?stub$"),
)

#: Exact template names (lowercase) that should always be removed.
TEMPLATES_TO_DELETE = frozenset(
    {
        "rtt",
        "#unlinkedwikibase",
        "about",
        "anchor",
        "defaultsort",
        "distinguish",
        "esborrany",
        "featured article",
        "fr",
        "good article",
        "italic title",
        "other uses",
        "redirect",
        "redirect-distinguish",
        "see also",
        "short description",
        "sprotect",
        "tedirect-distinguish",
        "toc limit",
        "use american english",
        "use dmy dates",
        "use mdy dates",
        "void",
    }
)

#: Infobox-like templates; content before the first one of these is dropped
#: by :func:`remove_lead_templates`.
_LEAD_INFOBOX_PREFIXES = ("{{infobox", "{{drugbox", "{{speciesbox")


def matches_deletion_pattern(name: str) -> bool:
    """Check if a template name matches one of the generic deletion patterns.

    :param name: The template name (lowercase).
    :return: True if the template should be deleted based on a pattern match.
    """
    return any(pattern.match(name) for pattern in TEMPLATE_DELETE_PATTERNS)


def check_temp_to_delete(name: str) -> bool:
    """Check if a template should be deleted based on its exact/prefix name.

    :param name: The template name (lowercase).
    :return: True if the template should be deleted, False otherwise.
    """
    if name.lower().startswith("defaultsort"):
        return True
    return name in TEMPLATES_TO_DELETE


def _should_delete(name: str) -> bool:
    return check_temp_to_delete(name) or name.startswith("#unlinkedwikibase") or matches_deletion_pattern(name)


def remove_templates(text: str) -> str:
    """Remove unwanted templates from wikitext.

    :param text: The wikitext to process.
    :return: The wikitext with unwanted templates removed.
    """
    if not text:
        return text

    parsed = wtp.parse(text)

    # Decide first, mutate second: removing an outer template invalidates
    # any templates nested inside it.
    targets = [t for t in parsed.templates if _should_delete(th.strip_name(t).lower())]

    for template in targets:
        try:
            template.string = ""
        except DeadIndexError:
            # Already removed along with a parent template.
            continue

    return parsed.string


def remove_lead_templates(text: str) -> str:
    """
    Remove content before infobox templates in the lead section.

    :param text: The wikitext to process.
    :return: The wikitext with content before the infobox removed.
    """
    # remove any thig before {{Infobox medical condition
    lowered = text.lower()

    for prefix in _LEAD_INFOBOX_PREFIXES:
        index = lowered.find(prefix)
        if index != -1:
            text = text[index:]
            break

    return text.strip()


__all__ = [
    "matches_deletion_pattern",
    "check_temp_to_delete",
    "remove_templates",
    "remove_lead_templates",
]
