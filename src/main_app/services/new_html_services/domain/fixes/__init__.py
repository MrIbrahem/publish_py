# from .media import remove_images
from __future__ import annotations

from .media import RemoveMissingImagesService, remove_videos
from .references import (
    del_empty_refs,
    remove_bad_refs,
)
from .structure import remove_categories
from .templates import (
    add_missing_title,
    remove_lead_templates,
    remove_templates,
)


class WikitextFixerService:
    def __init__(self) -> None:
        """
        init
        """

    def fix(self, text: str, title: str) -> str:
        """
        Port the full fix_wikitext pipeline from the original PHP tool:
            - remove_templates
            - remove_lead_templates
            - remove_bad_refs
            - del_empty_refs
            - remove_videos
            - remove_categories
            - remove_missing_images
            - add_missing_title
        """

        # Replace templates
        text = text.replace("{{drugbox", "{{Infobox drug")
        text = text.replace("{{Drugbox", "{{Infobox drug")

        # Clean up templates
        text = remove_templates(text)
        text = remove_lead_templates(text)

        # Clean up references
        text = remove_bad_refs(text)
        text = del_empty_refs(text)

        # text = remove_lang_links(text)

        # Remove videos
        text = remove_videos(text)

        # text = remove_images(text)

        # Remove categories
        text = remove_categories(text)

        # Handle missing images and add title
        service = RemoveMissingImagesService()

        text = service.remove_missing_images(text)
        text = add_missing_title(text, title)

        return text


__all__ = [
    "WikitextFixerService",
]
