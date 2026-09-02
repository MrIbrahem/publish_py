"""
Image and video removal utilities.

Port of ``src/Domain/Fixes/Media/FixImagesFixture.php``. Wikilinks are found
using ``wikitextparser`` instead of a manual regex, which correctly handles
nested wikilinks inside a caption (e.g. ``[[File:x.png|caption with a
[[link]] inside]]``) without the PHP pattern's fragile lookaround tricks.
"""

from __future__ import annotations

import posixpath

import wikitextparser as wtp

VIDEO_EXTENSIONS = {"webm", "ogv", "ogg", "mp4"}


def remove_images(text: str) -> str:
    """Wrap ``[[File:...]]`` image links in a ``{{subst:#ifexist:...}}`` check.

    :param text: The wikitext to process.
    :return: The wikitext with images wrapped in ``{{subst:#ifexist:...}}``.
    """
    if not text:
        return text

    parsed = wtp.parse(text)

    # Collect targets first: mutating a wikilink invalidates any wikilinks
    # nested inside it, so we must finish reading `.title`/`.string` from
    # every link before we start rewriting any of them.
    file_links = [link for link in parsed.wikilinks if link.title.strip().lower().startswith("file:")]
    targets = [(link, link.title.strip(), link.string) for link in file_links]

    for link, file_name, original in targets:
        link.string = f"{{{{subst:#ifexist:{file_name}|{original}}}}}"

    return str(parsed)


def remove_videos(text: str) -> str:
    """Remove video file links from wikitext.

    Removes tags like:
        - ``[[File:Schizophrenia video.webm|frameless|upright=1.36|Video explanation by Osmosis]]``
        - ``[[File:En.Wikipedia-VideoWiki-Schizophrenia.webm|thumb|thumbtime=2:25|upright=1.36|Video summary ([[Video:Schizophrenia|script]])]]``

    :param text: The wikitext to process.
    :return: The wikitext with video files removed.
    """
    if not text:
        return text

    parsed = wtp.parse(text)

    # Two-pass, for the same reason as in remove_images() above.
    to_remove = []
    for link in parsed.wikilinks:
        title = link.title.strip()
        if not title.lower().startswith("file:"):
            continue
        ext = posixpath.splitext(title)[1].lstrip(".").lower()
        if ext in VIDEO_EXTENSIONS:
            to_remove.append(link)

    for link in to_remove:
        link.string = ""

    return str(parsed)


__all__ = [
    "remove_images",
    "remove_videos",
]
