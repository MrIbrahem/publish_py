"""
Template parsing helpers.

This module replaces the old hand-rolled ``ParserTemplate``, ``ParserTemplates``
and ``Template`` PHP classes. Template parsing (including nested templates and
parameter extraction) is now delegated entirely to ``wikitextparser``
(the 5j9/wikitextparser library), which is a proper wikitext parser rather
than the regex-based recursive splitter the PHP code used.

Because wikitextparser's ``Template`` objects are "live" views into the
``WikiText`` object they were parsed from, editing a template (via
``set_arg`` / ``del_arg`` / assigning ``.string``) updates the parent text in
place. The idiomatic pattern used throughout the ``domain.fixes`` package is:

    parsed = wtp.parse(text)
    for template in parsed.templates:
        ...mutate template...
    new_text = parsed.string

The helpers below are thin convenience wrappers around that pattern so the
``fixes`` modules don't need to repeat the same small pieces of logic
(stripped names, trimmed parameter access, etc.) that the PHP ``Template``
class used to provide.
"""

from __future__ import annotations

import wikitextparser as wtp
from wikitextparser import Template, WikiText

try:  # DeadIndexError isn't part of wikitextparser's public API.
    from wikitextparser._wikitext import DeadIndexError
except ImportError:  # pragma: no cover - defensive, in case the private path moves
    DeadIndexError = Exception  # type: ignore[assignment,misc]


def parse(text: str) -> WikiText:
    """Parse wikitext and return the (mutable) WikiText object.

    Equivalent to calling ``wikitextparser.parse`` directly; provided here so
    callers only need to import this module. Keep a reference to the
    returned object and call ``parsed.string`` after mutating any of its
    templates to get the updated text back.
    """
    return wtp.parse(text or "")


def get_templates(text: str) -> list[Template]:
    """Return all templates (including nested ones) found in ``text``.

    Equivalent of the old PHP ``get_templates()`` helper. NOTE: the returned
    ``Template`` objects are tied to a fresh, internal ``WikiText`` object.
    If you need the edited text back afterwards, use :func:`parse` yourself
    and iterate ``parsed.templates`` instead, e.g.::

        parsed = parse(text)
        for template in parsed.templates:
            ...
        text = parsed.string
    """
    if not text:
        return []
    return wtp.parse(text).templates


def strip_name(template: Template) -> str:
    """Equivalent of PHP's ``Template::getStripName()``.

    Underscores are treated as spaces and the result is trimmed, matching
    MediaWiki's template name normalization.
    """
    try:
        return template.name.strip().replace("_", " ")
    except DeadIndexError:
        return ""

def get_parameter(template: Template, key: str, default: str = "") -> str:
    """Equivalent of PHP's ``Template::getParameter($key, $default)``."""
    arg = template.get_arg(key)
    if arg is None:
        return default
    return arg.value.strip()


def has_parameter(template: Template, key: str) -> bool:
    """Equivalent of PHP's ``array_key_exists($key, $template->getParameters())``."""
    return template.get_arg(key) is not None


def set_parameter(template: Template, key: str, value: str, preserve_spacing: bool = True) -> None:
    """Equivalent of PHP's ``Template::setParameter($key, $value)``."""
    template.set_arg(key, value, preserve_spacing=preserve_spacing)


def delete_parameter(template: Template, key: str) -> None:
    """Equivalent of PHP's ``Template::deleteParameter($key)``. No-op if absent."""
    if template.get_arg(key) is not None:
        template.del_arg(key)


def get_parameters(template: Template) -> dict[str, str]:
    """Return all parameters as a ``{name: value}`` dict (values trimmed).

    Positional parameters are keyed by their 1-based position as a string,
    matching how MediaWiki (and the old PHP code) addresses them.
    """
    params: dict[str, str] = {}
    for arg in template.arguments:
        name = arg.name.strip()
        params[name] = arg.value.strip()
    return params


def render_pretty(template: Template, ljust: int = 0) -> str:
    """Render a template on multiple lines, one parameter per line.

    Equivalent of PHP's ``Template::toString($newLine = true, $ljust)``:
    positional parameters stay inline (``|value``), named parameters each
    get their own line (``\\n|key=value``), and parameter names can be
    left-padded to ``ljust`` characters for visual alignment.

    :param template: The template to render.
    :param ljust: Left-justify parameter names to this width (0 disables padding).
    :return: The pretty-printed template text (does NOT mutate ``template``).
    """
    name = template.name.strip()
    result = "{{" + name
    for arg in template.arguments:
        value = arg.value.strip()
        if arg.positional:
            result += "|" + value
        else:
            key = arg.name.strip()
            key_fmt = key.ljust(ljust) if ljust > 0 else key
            result += "\n|" + key_fmt + "=" + value
    result += "\n}}"
    return result


def get_arg_number(param_name: str, prefix: str) -> str | None:
    """Extract the numeric suffix from a parameter name like ``image2``.

    Returns ``""`` for the bare ``prefix`` (e.g. ``image``), the digits for
    ``prefix2``, ``prefix10`` etc., or ``None`` if ``param_name`` doesn't
    match ``prefix`` followed by only digits.
    """
    name = param_name.strip().lower()
    prefix = prefix.lower()
    if not name.startswith(prefix):
        return None
    suffix = name[len(prefix) :]
    if suffix == "" or suffix.isdigit():
        return suffix
    return None


__all__ = [
    "parse",
    "get_templates",
    "strip_name",
    "get_parameter",
    "has_parameter",
    "set_parameter",
    "delete_parameter",
    "get_parameters",
    "render_pretty",
    "get_arg_number",
]
